from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *

# Auto-generated viewsets for ethical_ai_oversight
# ViewSets will be created based on models
