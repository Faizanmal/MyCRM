"""
Mobile App Enhancement Services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import openai
import json
import math


class OfflineSyncService:
    """Service for handling offline sync operations"""
    
    def __init__(self, user):
        self.user = user
    
    def register_device(
        self,
        device_id: str,
        device_name: str,
        platform: str,
        os_version: str = '',
        app_version: str = '',
        push_token: str = '',
        push_provider: str = ''
    ) -> Dict[str, Any]:
        """Register a device for sync"""
        from .mobile_models import DeviceRegistration
        
        device, created = DeviceRegistration.objects.update_or_create(
            device_id=device_id,
            defaults={
                'user': self.user,
                'device_name': device_name,
                'platform': platform,
                'os_version': os_version,
                'app_version': app_version,
                'push_token': push_token,
                'push_provider': push_provider,
                'is_active': True,
                'last_active_at': timezone.now()
            }
        )
        
        return {
            'device_id': device.device_id,
            'registered': True,
            'created': created
        }
    
    def get_pending_changes(
        self,
        device_id: str,
        since_timestamp: datetime = None,
        entity_types: List[str] = None
    ) -> Dict[str, Any]:
        """Get changes since last sync for a device"""
        from .mobile_models import DeviceRegistration
        
        device = DeviceRegistration.objects.get(
            device_id=device_id, user=self.user
        )
        
        since = since_timestamp or device.last_sync_at or timezone.now() - timedelta(days=30)
        
        changes = {
            'contacts': [],
            'leads': [],
            'opportunities': [],
            'tasks': [],
            'activities': []
        }
        
        # Query each entity type for changes
        if not entity_types or 'contacts' in entity_types:
            from contact_management.models import Contact
            contacts = Contact.objects.filter(
                updated_at__gt=since
            ).values('id', 'first_name', 'last_name', 'email', 'phone', 'updated_at')
            changes['contacts'] = list(contacts)
        
        if not entity_types or 'leads' in entity_types:
            from lead_management.models import Lead
            leads = Lead.objects.filter(
                updated_at__gt=since
            ).values('id', 'name', 'email', 'status', 'updated_at')
            changes['leads'] = list(leads)
        
        if not entity_types or 'opportunities' in entity_types:
            from opportunity_management.models import Opportunity
            opportunities = Opportunity.objects.filter(
                updated_at__gt=since
            ).values('id', 'name', 'value', 'stage', 'updated_at')
            changes['opportunities'] = list(opportunities)
        
        if not entity_types or 'tasks' in entity_types:
            from task_management.models import Task
            tasks = Task.objects.filter(
                assigned_to=self.user,
                updated_at__gt=since
            ).values('id', 'title', 'status', 'due_date', 'updated_at')
            changes['tasks'] = list(tasks)
        
        return {
            'since': since.isoformat(),
            'changes': changes,
            'total_changes': sum(len(v) for v in changes.values())
        }
    
    def queue_sync_operation(
        self,
        device_id: str,
        operation: str,
        entity_type: str,
        entity_id: str,
        payload: Dict[str, Any],
        local_timestamp: datetime
    ) -> Dict[str, Any]:
        """Queue an offline operation for sync"""
        from .mobile_models import OfflineSyncQueue
        
        sync_item = OfflineSyncQueue.objects.create(
            user=self.user,
            device_id=device_id,
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            local_timestamp=local_timestamp,
            status='pending'
        )
        
        return {
            'sync_id': str(sync_item.id),
            'queued': True
        }
    
    def process_sync_queue(
        self, device_id: str
    ) -> Dict[str, Any]:
        """Process pending sync operations"""
        from .mobile_models import OfflineSyncQueue
        
        pending = OfflineSyncQueue.objects.filter(
            user=self.user,
            device_id=device_id,
            status='pending'
        ).order_by('local_timestamp')
        
        results = {
            'processed': 0,
            'conflicts': 0,
            'failed': 0,
            'details': []
        }
        
        for item in pending:
            try:
                result = self._process_sync_item(item)
                
                if result['status'] == 'synced':
                    results['processed'] += 1
                elif result['status'] == 'conflict':
                    results['conflicts'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'sync_id': str(item.id),
                    'entity': f"{item.entity_type}/{item.entity_id}",
                    'result': result
                })
                
            except Exception as e:
                item.status = 'failed'
                item.error_message = str(e)
                item.retry_count += 1
                item.save()
                
                results['failed'] += 1
                results['details'].append({
                    'sync_id': str(item.id),
                    'error': str(e)
                })
        
        # Update device last sync time
        from .mobile_models import DeviceRegistration
        DeviceRegistration.objects.filter(
            device_id=device_id, user=self.user
        ).update(last_sync_at=timezone.now())
        
        return results
    
    def _process_sync_item(self, item) -> Dict[str, Any]:
        """Process a single sync item"""
        # Check for conflicts
        server_entity = self._get_entity(item.entity_type, item.entity_id)
        
        if server_entity:
            server_updated = getattr(server_entity, 'updated_at', None)
            
            if server_updated and server_updated > item.local_timestamp:
                # Conflict detected
                item.status = 'conflict'
                item.conflict_data = self._serialize_entity(server_entity)
                item.save()
                
                return {
                    'status': 'conflict',
                    'server_data': item.conflict_data,
                    'client_data': item.payload
                }
        
        # Apply the operation
        if item.operation == 'create':
            self._create_entity(item.entity_type, item.payload)
        elif item.operation == 'update':
            self._update_entity(item.entity_type, item.entity_id, item.payload)
        elif item.operation == 'delete':
            self._delete_entity(item.entity_type, item.entity_id)
        
        item.status = 'synced'
        item.server_timestamp = timezone.now()
        item.save()
        
        return {'status': 'synced'}
    
    def _get_entity(self, entity_type: str, entity_id: str):
        """Get an entity by type and ID"""
        model_map = {
            'Contact': 'contact_management.models.Contact',
            'Lead': 'lead_management.models.Lead',
            'Opportunity': 'opportunity_management.models.Opportunity',
            'Task': 'task_management.models.Task',
        }
        
        if entity_type not in model_map:
            return None
        
        try:
            module_path, class_name = model_map[entity_type].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            model_class = getattr(module, class_name)
            return model_class.objects.get(id=entity_id)
        except:
            return None
    
    def _serialize_entity(self, entity) -> Dict[str, Any]:
        """Serialize an entity for conflict resolution"""
        from django.forms.models import model_to_dict
        return model_to_dict(entity)
    
    def _create_entity(self, entity_type: str, payload: Dict[str, Any]):
        """Create a new entity"""
        # Implementation depends on entity type
        pass
    
    def _update_entity(
        self, entity_type: str, entity_id: str, payload: Dict[str, Any]
    ):
        """Update an existing entity"""
        entity = self._get_entity(entity_type, entity_id)
        if entity:
            for key, value in payload.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            entity.save()
    
    def _delete_entity(self, entity_type: str, entity_id: str):
        """Delete an entity"""
        entity = self._get_entity(entity_type, entity_id)
        if entity:
            entity.delete()
    
    def resolve_conflict(
        self,
        sync_id: str,
        resolution: str,  # 'client_wins', 'server_wins', 'merged'
        merged_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Resolve a sync conflict"""
        from .mobile_models import OfflineSyncQueue
        
        item = OfflineSyncQueue.objects.get(
            id=sync_id, user=self.user, status='conflict'
        )
        
        if resolution == 'client_wins':
            # Apply client data
            self._update_entity(
                item.entity_type, item.entity_id, item.payload
            )
        elif resolution == 'merged' and merged_data:
            # Apply merged data
            self._update_entity(
                item.entity_type, item.entity_id, merged_data
            )
        # server_wins: no action needed
        
        item.status = 'synced'
        item.resolution = resolution
        item.server_timestamp = timezone.now()
        item.save()
        
        return {
            'sync_id': sync_id,
            'resolution': resolution,
            'resolved': True
        }


class BusinessCardScanService:
    """Service for processing business card scans"""
    
    def __init__(self, user):
        self.user = user
    
    def process_card(
        self,
        image_url: str,
        scan_location: Dict[str, Any] = None,
        event_name: str = ''
    ) -> Dict[str, Any]:
        """Process a business card image"""
        from .mobile_models import BusinessCardScan
        
        scan = BusinessCardScan.objects.create(
            user=self.user,
            image_url=image_url,
            scan_location=scan_location,
            event_name=event_name,
            status='processing'
        )
        
        try:
            # Extract text using OCR (simulated)
            raw_text = self._perform_ocr(image_url)
            scan.raw_text = raw_text
            
            # Extract structured data using AI
            extracted = self._extract_data_ai(raw_text)
            
            scan.extracted_data = extracted
            scan.name = extracted.get('name', '')
            scan.title = extracted.get('title', '')
            scan.company = extracted.get('company', '')
            scan.email = extracted.get('email', '')
            scan.phone = extracted.get('phone', '')
            scan.mobile = extracted.get('mobile', '')
            scan.address = extracted.get('address', '')
            scan.website = extracted.get('website', '')
            scan.linkedin = extracted.get('linkedin', '')
            
            scan.confidence_scores = extracted.get('confidence', {})
            scan.overall_confidence = extracted.get('overall_confidence', 0)
            
            # Set status based on confidence
            if scan.overall_confidence >= 80:
                scan.status = 'completed'
            elif scan.overall_confidence >= 50:
                scan.status = 'review'
            else:
                scan.status = 'failed'
            
            scan.save()
            
            return {
                'scan_id': str(scan.id),
                'status': scan.status,
                'extracted_data': extracted,
                'confidence': float(scan.overall_confidence)
            }
            
        except Exception as e:
            scan.status = 'failed'
            scan.save()
            
            return {
                'scan_id': str(scan.id),
                'status': 'failed',
                'error': str(e)
            }
    
    def _perform_ocr(self, image_url: str) -> str:
        """Perform OCR on image (simplified)"""
        # In production, integrate with OCR service like Google Vision, AWS Textract
        return ""
    
    def _extract_data_ai(self, text: str) -> Dict[str, Any]:
        """Extract structured data from text using AI"""
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Extract contact information from business card text.
                        Return JSON with: name, title, company, email, phone, mobile, 
                        address, website, linkedin, and confidence scores (0-100) for each field."""
                    },
                    {
                        "role": "user",
                        "content": f"Extract contact info from:\n{text}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception:
            return {
                'name': '', 'title': '', 'company': '', 'email': '',
                'phone': '', 'mobile': '', 'address': '', 'website': '',
                'linkedin': '', 'confidence': {}, 'overall_confidence': 0
            }
    
    def create_contact_from_scan(
        self,
        scan_id: str,
        overrides: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a contact from a business card scan"""
        from .mobile_models import BusinessCardScan
        from contact_management.models import Contact
        
        scan = BusinessCardScan.objects.get(id=scan_id, user=self.user)
        
        # Merge extracted data with overrides
        data = {
            'first_name': scan.name.split()[0] if scan.name else '',
            'last_name': ' '.join(scan.name.split()[1:]) if scan.name else '',
            'title': scan.title,
            'company': scan.company,
            'email': scan.email,
            'phone': scan.phone,
            'mobile': scan.mobile,
            'address': scan.address,
            'website': scan.website,
            'linkedin': scan.linkedin,
        }
        
        if overrides:
            data.update(overrides)
        
        # Create contact
        contact = Contact.objects.create(**data)
        
        scan.created_contact = contact
        scan.save(update_fields=['created_contact'])
        
        return {
            'scan_id': str(scan.id),
            'contact_id': str(contact.id),
            'created': True
        }


class LocationService:
    """Service for location-based features"""
    
    def __init__(self, user):
        self.user = user
    
    def check_in(
        self,
        latitude: float,
        longitude: float,
        check_in_type: str,
        accuracy_meters: int = None,
        notes: str = '',
        photos: List[str] = None,
        contact_id: str = None,
        lead_id: str = None,
        opportunity_id: str = None
    ) -> Dict[str, Any]:
        """Record a location check-in"""
        from .mobile_models import LocationCheckIn
        
        # Reverse geocode (simplified)
        address_info = self._reverse_geocode(latitude, longitude)
        
        check_in = LocationCheckIn.objects.create(
            user=self.user,
            latitude=latitude,
            longitude=longitude,
            accuracy_meters=accuracy_meters,
            address=address_info.get('address', ''),
            city=address_info.get('city', ''),
            state=address_info.get('state', ''),
            country=address_info.get('country', ''),
            postal_code=address_info.get('postal_code', ''),
            check_in_type=check_in_type,
            notes=notes,
            photos=photos or [],
            check_in_time=timezone.now(),
            contact_id=contact_id,
            lead_id=lead_id,
            opportunity_id=opportunity_id
        )
        
        # Create activity
        self._create_check_in_activity(check_in)
        
        return {
            'check_in_id': str(check_in.id),
            'address': check_in.address,
            'city': check_in.city,
            'check_in_time': check_in.check_in_time.isoformat()
        }
    
    def check_out(self, check_in_id: str) -> Dict[str, Any]:
        """Record check-out"""
        from .mobile_models import LocationCheckIn
        
        check_in = LocationCheckIn.objects.get(
            id=check_in_id, user=self.user
        )
        
        check_in.check_out_time = timezone.now()
        check_in.duration_minutes = int(
            (check_in.check_out_time - check_in.check_in_time).total_seconds() / 60
        )
        check_in.save()
        
        return {
            'check_in_id': str(check_in.id),
            'duration_minutes': check_in.duration_minutes
        }
    
    def _reverse_geocode(
        self, latitude: float, longitude: float
    ) -> Dict[str, Any]:
        """Reverse geocode coordinates to address"""
        # In production, use Google Maps, Mapbox, etc.
        return {
            'address': '',
            'city': '',
            'state': '',
            'country': '',
            'postal_code': ''
        }
    
    def _create_check_in_activity(self, check_in):
        """Create an activity for the check-in"""
        # Create activity record
        pass
    
    def find_nearby_customers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Find nearby customers and leads"""
        from .mobile_models import NearbyCustomer
        
        # Check cache first
        if use_cache:
            cache = NearbyCustomer.objects.filter(
                user=self.user,
                center_latitude=latitude,
                center_longitude=longitude,
                radius_km=radius_km,
                expires_at__gt=timezone.now()
            ).first()
            
            if cache:
                return {
                    'customers': cache.customers,
                    'leads': cache.leads,
                    'from_cache': True
                }
        
        # Query nearby entities
        nearby_customers = self._find_entities_in_radius(
            'contact_management.Contact', latitude, longitude, radius_km
        )
        nearby_leads = self._find_entities_in_radius(
            'lead_management.Lead', latitude, longitude, radius_km
        )
        
        # Cache results
        NearbyCustomer.objects.create(
            user=self.user,
            center_latitude=latitude,
            center_longitude=longitude,
            radius_km=radius_km,
            customers=nearby_customers,
            leads=nearby_leads,
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        
        return {
            'customers': nearby_customers,
            'leads': nearby_leads,
            'from_cache': False
        }
    
    def _find_entities_in_radius(
        self,
        model_path: str,
        lat: float,
        lon: float,
        radius_km: float
    ) -> List[Dict[str, Any]]:
        """Find entities within radius using Haversine formula"""
        # Simplified - in production use PostGIS or similar
        
        # Convert radius to approximate lat/lon bounds
        lat_range = radius_km / 111.0
        lon_range = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        try:
            module_path, class_name = model_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            model_class = getattr(module, class_name)
            
            # Query with bounding box (approximate)
            entities = model_class.objects.filter(
                latitude__range=(lat - lat_range, lat + lat_range),
                longitude__range=(lon - lon_range, lon + lon_range)
            )[:50]
            
            results = []
            for entity in entities:
                distance = self._haversine_distance(
                    lat, lon,
                    float(entity.latitude), float(entity.longitude)
                )
                
                if distance <= radius_km:
                    results.append({
                        'id': str(entity.id),
                        'name': getattr(entity, 'name', str(entity)),
                        'distance_km': round(distance, 2),
                        'latitude': float(entity.latitude),
                        'longitude': float(entity.longitude)
                    })
            
            return sorted(results, key=lambda x: x['distance_km'])
            
        except Exception:
            return []
    
    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_route_optimization(
        self,
        locations: List[Dict[str, Any]],
        start_location: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Optimize route for multiple visits"""
        # Simple nearest-neighbor algorithm
        if not locations:
            return {'optimized_route': [], 'total_distance_km': 0}
        
        if start_location:
            current = (start_location['latitude'], start_location['longitude'])
        else:
            current = (
                locations[0]['latitude'], locations[0]['longitude']
            )
        
        remaining = list(locations)
        route = []
        total_distance = 0
        
        while remaining:
            nearest = None
            nearest_distance = float('inf')
            
            for loc in remaining:
                dist = self._haversine_distance(
                    current[0], current[1],
                    loc['latitude'], loc['longitude']
                )
                if dist < nearest_distance:
                    nearest = loc
                    nearest_distance = dist
            
            if nearest:
                route.append({
                    **nearest,
                    'distance_from_previous': round(nearest_distance, 2)
                })
                total_distance += nearest_distance
                current = (nearest['latitude'], nearest['longitude'])
                remaining.remove(nearest)
        
        return {
            'optimized_route': route,
            'total_distance_km': round(total_distance, 2),
            'estimated_travel_time_minutes': round(total_distance * 2, 0)
        }


class VoiceNoteService:
    """Service for processing voice notes"""
    
    def __init__(self, user):
        self.user = user
    
    def process_voice_note(
        self,
        audio_url: str,
        duration_seconds: int,
        format: str = 'm4a',
        title: str = '',
        contact_id: str = None,
        lead_id: str = None,
        opportunity_id: str = None,
        recorded_location: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a voice note recording"""
        from .mobile_models import VoiceNote
        
        note = VoiceNote.objects.create(
            user=self.user,
            audio_url=audio_url,
            duration_seconds=duration_seconds,
            format=format,
            title=title,
            contact_id=contact_id,
            lead_id=lead_id,
            opportunity_id=opportunity_id,
            recorded_location=recorded_location,
            status='processing'
        )
        
        try:
            # Transcribe audio
            transcription = self._transcribe_audio(audio_url)
            note.transcription = transcription
            
            # Analyze with AI
            analysis = self._analyze_transcription(transcription)
            note.summary = analysis.get('summary', '')
            note.action_items = analysis.get('action_items', [])
            note.entities = analysis.get('entities', [])
            
            note.status = 'transcribed'
            note.save()
            
            # Auto-create tasks from action items
            created_tasks = []
            for item in note.action_items:
                task_id = self._create_task_from_action_item(item, note)
                if task_id:
                    created_tasks.append(task_id)
            
            note.created_tasks = created_tasks
            note.save(update_fields=['created_tasks'])
            
            return {
                'voice_note_id': str(note.id),
                'status': 'transcribed',
                'summary': note.summary,
                'action_items': note.action_items,
                'created_tasks': created_tasks
            }
            
        except Exception as e:
            note.status = 'failed'
            note.save()
            
            return {
                'voice_note_id': str(note.id),
                'status': 'failed',
                'error': str(e)
            }
    
    def _transcribe_audio(self, audio_url: str) -> str:
        """Transcribe audio to text"""
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # In production, download audio and send to Whisper API
            # Simplified for now
            return ""
            
        except Exception:
            return ""
    
    def _analyze_transcription(self, text: str) -> Dict[str, Any]:
        """Analyze transcription for summary and action items"""
        if not text:
            return {'summary': '', 'action_items': [], 'entities': []}
        
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze this voice note transcription and extract:
                        1. A brief summary (2-3 sentences)
                        2. Action items (tasks that need to be done)
                        3. Entities mentioned (people, companies, dates)
                        
                        Return as JSON with keys: summary, action_items, entities"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception:
            return {'summary': '', 'action_items': [], 'entities': []}
    
    def _create_task_from_action_item(
        self, action_item: Dict[str, Any], note
    ) -> Optional[str]:
        """Create a task from an action item"""
        try:
            from task_management.models import Task
            
            task = Task.objects.create(
                title=action_item.get('task', action_item.get('title', '')),
                description=f"From voice note: {note.title or 'Untitled'}",
                assigned_to=self.user,
                due_date=action_item.get('due_date'),
                contact_id=note.contact_id,
                lead_id=note.lead_id,
                opportunity_id=note.opportunity_id
            )
            
            return str(task.id)
            
        except Exception:
            return None
