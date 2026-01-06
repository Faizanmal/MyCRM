class Contact {
  final int? id;
  final String firstName;
  final String lastName;
  final String? email;
  final String? phone;
  final String? company;
  final String? position;
  final String? status;
  final String? address;
  final String? website;
  final String? notes;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  
  Contact({
    this.id,
    required this.firstName,
    required this.lastName,
    this.email,
    this.phone,
    this.company,
    this.position,
    this.status,
    this.address,
    this.website,
    this.notes,
    this.createdAt,
    this.updatedAt,
  });
  
  String get fullName => '$firstName $lastName';
  
  String get initials => '${firstName[0]}${lastName[0]}'.toUpperCase();
  
  factory Contact.fromJson(Map<String, dynamic> json) {
    return Contact(
      id: json['id'],
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      email: json['email'],
      phone: json['phone'],
      company: json['company'],
      position: json['position'],
      status: json['status'],
      address: json['address'],
      website: json['website'],
      notes: json['notes'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone': phone,
      'company': company,
      'position': position,
      'status': status,
      'address': address,
      'website': website,
      'notes': notes,
    };
  }
}

class Lead {
  final int? id;
  final String firstName;
  final String lastName;
  final String? email;
  final String? phone;
  final String? company;
  final String? source;
  final String? status;
  final int? score;
  final String? notes;
  final String? title;
  final String? description;
  final double? estimatedValue;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  
  Lead({
    this.id,
    required this.firstName,
    required this.lastName,
    this.email,
    this.phone,
    this.company,
    this.source,
    this.status,
    this.score,
    this.notes,
    this.title,
    this.description,
    this.estimatedValue,
    this.createdAt,
    this.updatedAt,
  });
  
  String get fullName => '$firstName $lastName';
  
  String get initials => '${firstName[0]}${lastName[0]}'.toUpperCase();
  
  factory Lead.fromJson(Map<String, dynamic> json) {
    return Lead(
      id: json['id'],
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      email: json['email'],
      phone: json['phone'],
      company: json['company'],
      source: json['source'],
      status: json['status'],
      score: json['score'],
      notes: json['notes'],
      title: json['title'],
      description: json['description'],
      estimatedValue: json['estimated_value'] != null 
          ? double.tryParse(json['estimated_value'].toString()) 
          : null,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone': phone,
      'company': company,
      'source': source,
      'status': status,
      'score': score,
      'notes': notes,
      'title': title,
      'description': description,
      'estimated_value': estimatedValue,
    };
  }
}

class Opportunity {
  final int? id;
  final String name;
  final double? amount;
  final String? stage;
  final double? probability;
  final DateTime? closeDate;
  final int? contactId;
  final String? contactName;
  final String? description;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  
  Opportunity({
    this.id,
    required this.name,
    this.amount,
    this.stage,
    this.probability,
    this.closeDate,
    this.contactId,
    this.contactName,
    this.description,
    this.createdAt,
    this.updatedAt,
  });
  
  factory Opportunity.fromJson(Map<String, dynamic> json) {
    return Opportunity(
      id: json['id'],
      name: json['name'] ?? '',
      amount: json['amount']?.toDouble(),
      stage: json['stage'],
      probability: json['probability']?.toDouble(),
      closeDate: json['close_date'] != null 
          ? DateTime.parse(json['close_date']) 
          : null,
      contactId: json['contact'],
      contactName: json['contact_name'],
      description: json['description'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'name': name,
      'amount': amount,
      'stage': stage,
      'probability': probability,
      'close_date': closeDate?.toIso8601String(),
      'contact': contactId,
      'description': description,
    };
  }
}

class Task {
  final int? id;
  final String title;
  final String? description;
  final String? status;
  final String? priority;
  final DateTime? dueDate;
  final int? assignedToId;
  final String? assignedToName;
  final int? contactId;
  final String? contactName;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  
  Task({
    this.id,
    required this.title,
    this.description,
    this.status,
    this.priority,
    this.dueDate,
    this.assignedToId,
    this.assignedToName,
    this.contactId,
    this.contactName,
    this.createdAt,
    this.updatedAt,
  });
  
  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'],
      title: json['title'] ?? '',
      description: json['description'],
      status: json['status'],
      priority: json['priority'],
      dueDate: json['due_date'] != null 
          ? DateTime.parse(json['due_date']) 
          : null,
      assignedToId: json['assigned_to'],
      assignedToName: json['assigned_to_name'],
      contactId: json['contact'],
      contactName: json['contact_name'],
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'description': description,
      'status': status,
      'priority': priority,
      'due_date': dueDate?.toIso8601String(),
      'assigned_to': assignedToId,
      'contact': contactId,
    };
  }
}
