import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../models/crm_models.dart';

class TaskDetailScreen extends StatefulWidget {
  final Task task;
  
  const TaskDetailScreen({super.key, required this.task});
  
  @override
  State<TaskDetailScreen> createState() => _TaskDetailScreenState();
}

class _TaskDetailScreenState extends State<TaskDetailScreen> {
  late Task _task;
  bool _isEditing = false;
  
  late TextEditingController _titleController;
  late TextEditingController _descriptionController;
  
  @override
  void initState() {
    super.initState();
    _task = widget.task;
    _initControllers();
  }
  
  void _initControllers() {
    _titleController = TextEditingController(text: _task.title);
    _descriptionController = TextEditingController(text: _task.description ?? '');
  }
  
  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }
  
  Color _getPriorityColor(String? priority) {
    switch (priority?.toLowerCase()) {
      case 'high':
        return AppColors.error;
      case 'medium':
        return AppColors.warning;
      case 'low':
        return AppColors.success;
      default:
        return AppColors.grey500;
    }
  }
  
  Color _getStatusColor(String? status) {
    switch (status?.toLowerCase()) {
      case 'completed':
        return AppColors.success;
      case 'in_progress':
        return AppColors.primary;
      case 'pending':
        return AppColors.warning;
      case 'cancelled':
        return AppColors.grey500;
      default:
        return AppColors.info;
    }
  }
  
  IconData _getStatusIcon(String? status) {
    switch (status?.toLowerCase()) {
      case 'completed':
        return Icons.check_circle;
      case 'in_progress':
        return Icons.play_circle;
      case 'pending':
        return Icons.pending;
      case 'cancelled':
        return Icons.cancel;
      default:
        return Icons.radio_button_unchecked;
    }
  }
  
  Future<void> _toggleComplete() async {
    setState(() {
      // Toggle between completed and pending
      if (_task.status == 'completed') {
        _task = Task(
          id: _task.id,
          title: _task.title,
          description: _task.description,
          dueDate: _task.dueDate,
          priority: _task.priority,
          status: 'pending',
        );
      } else {
        _task = Task(
          id: _task.id,
          title: _task.title,
          description: _task.description,
          dueDate: _task.dueDate,
          priority: _task.priority,
          status: 'completed',
        );
      }
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _task.status == 'completed' ? 'Task marked complete' : 'Task marked incomplete',
        ),
        backgroundColor: _task.status == 'completed' ? AppColors.success : AppColors.warning,
      ),
    );
  }
  
  Future<void> _deleteTask() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Task'),
        content: Text('Are you sure you want to delete "${_task.title}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    
    if (confirmed == true && mounted) {
      Navigator.pop(context, true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Task deleted'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Edit Task' : 'Task Details'),
        actions: [
          if (!_isEditing)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => setState(() => _isEditing = true),
            ),
          if (_isEditing)
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () {
                setState(() => _isEditing = false);
                _initControllers();
              },
            ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'delete') {
                _deleteTask();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete, color: AppColors.error),
                    SizedBox(width: 8),
                    Text('Delete', style: TextStyle(color: AppColors.error)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status and Priority Header
            _buildStatusHeader(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Task Details
            _buildDetailsSection(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Due Date Section
            _buildDueDateSection(),
            const SizedBox(height: AppSizes.paddingLg),
            
            // Actions
            if (!_isEditing) _buildActionsSection(),
            
            if (_isEditing) ...[
              const SizedBox(height: AppSizes.paddingLg),
              _buildSaveButton(),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatusHeader() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Row(
          children: [
            Expanded(
              child: Column(
                children: [
                  const Text(
                    'Status',
                    style: TextStyle(fontSize: AppSizes.fontSm, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        _getStatusIcon(_task.status),
                        color: _getStatusColor(_task.status),
                        size: 24,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _task.status?.replaceAll('_', ' ').toUpperCase() ?? 'PENDING',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: _getStatusColor(_task.status),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Container(
              width: 1,
              height: 50,
              color: AppColors.grey200,
            ),
            Expanded(
              child: Column(
                children: [
                  const Text(
                    'Priority',
                    style: TextStyle(fontSize: AppSizes.fontSm, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSizes.paddingSm,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getPriorityColor(_task.priority).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                      border: Border.all(
                        color: _getPriorityColor(_task.priority).withValues(alpha: 0.3),
                      ),
                    ),
                    child: Text(
                      _task.priority?.toUpperCase() ?? 'MEDIUM',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: _getPriorityColor(_task.priority),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildDetailsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Task Details',
              style: TextStyle(
                fontSize: AppSizes.fontLg,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppSizes.paddingMd),
            
            if (_isEditing) ...[
              TextField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: 'Title',
                  border: OutlineInputBorder(),
                ),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: AppSizes.paddingSm),
              TextField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                maxLines: 4,
              ),
            ] else ...[
              Text(
                _task.title,
                style: const TextStyle(
                  fontSize: AppSizes.fontLg,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (_task.description != null) ...[
                const SizedBox(height: AppSizes.paddingSm),
                Text(
                  _task.description!,
                  style: TextStyle(
                    fontSize: AppSizes.fontMd,
                    color: AppColors.grey600,
                  ),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildDueDateSection() {
    final isOverdue = _task.dueDate != null && 
        _task.dueDate!.isBefore(DateTime.now()) && 
        _task.status != 'completed';
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.paddingMd),
        child: Row(
          children: [
            Icon(
              Icons.calendar_today,
              color: isOverdue ? AppColors.error : AppColors.grey500,
            ),
            const SizedBox(width: AppSizes.paddingSm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Due Date',
                    style: TextStyle(
                      fontSize: AppSizes.fontSm,
                      color: Colors.grey,
                    ),
                  ),
                  Text(
                    _task.dueDate != null
                        ? '${_task.dueDate!.day}/${_task.dueDate!.month}/${_task.dueDate!.year}'
                        : 'No due date set',
                    style: TextStyle(
                      fontSize: AppSizes.fontMd,
                      fontWeight: FontWeight.w600,
                      color: isOverdue ? AppColors.error : null,
                    ),
                  ),
                ],
              ),
            ),
            if (isOverdue)
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 8,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: AppColors.error.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'OVERDUE',
                  style: TextStyle(
                    fontSize: AppSizes.fontXs,
                    fontWeight: FontWeight.bold,
                    color: AppColors.error,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildActionsSection() {
    final isCompleted = _task.status == 'completed';
    
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _toggleComplete,
            icon: Icon(isCompleted ? Icons.replay : Icons.check),
            label: Text(isCompleted ? 'Mark Incomplete' : 'Mark Complete'),
            style: ElevatedButton.styleFrom(
              backgroundColor: isCompleted ? AppColors.warning : AppColors.success,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              ),
            ),
          ),
        ),
      ],
    );
  }
  
  Widget _buildSaveButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () {
          setState(() => _isEditing = false);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Task updated successfully'),
              backgroundColor: AppColors.success,
            ),
          );
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: AppSizes.paddingMd),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSizes.radiusMd),
          ),
        ),
        child: const Text(
          'Save Changes',
          style: TextStyle(
            fontSize: AppSizes.fontMd,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
