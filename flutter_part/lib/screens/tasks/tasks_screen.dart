import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';
import '../../core/utils/date_formatter.dart';
import '../../models/crm_models.dart';
import 'task_detail_screen.dart';
import 'add_task_screen.dart';

class TasksScreen extends StatefulWidget {
  const TasksScreen({super.key});
  
  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen> {
  List<Task> _tasks = [];
  bool _isLoading = true;
  String _filterStatus = 'All';
  
  @override
  void initState() {
    super.initState();
    _loadTasks();
  }
  
  Future<void> _loadTasks() async {
    setState(() => _isLoading = true);
    
    await Future.delayed(const Duration(milliseconds: 800));
    
    setState(() {
      _tasks = [
        Task(
          id: 1,
          title: 'Follow up with John Doe',
          description: 'Discuss enterprise software requirements',
          status: 'To Do',
          priority: 'High',
          dueDate: DateTime.now().add(const Duration(days: 1)),
          contactName: 'John Doe',
        ),
        Task(
          id: 2,
          title: 'Prepare proposal for Jane Smith',
          description: 'Marketing campaign proposal',
          status: 'In Progress',
          priority: 'Medium',
          dueDate: DateTime.now().add(const Duration(days: 3)),
          contactName: 'Jane Smith',
        ),
        Task(
          id: 3,
          title: 'Schedule demo call',
          description: 'Product demo for Bob Johnson',
          status: 'To Do',
          priority: 'Low',
          dueDate: DateTime.now().add(const Duration(days: 7)),
          contactName: 'Bob Johnson',
        ),
        Task(
          id: 4,
          title: 'Send contract',
          description: 'Final contract for review',
          status: 'Completed',
          priority: 'Urgent',
          dueDate: DateTime.now().subtract(const Duration(days: 1)),
          contactName: 'Alice Williams',
        ),
      ];
      _isLoading = false;
    });
  }
  
  List<Task> get _filteredTasks {
    if (_filterStatus == 'All') return _tasks;
    return _tasks.where((task) => task.status == _filterStatus).toList();
  }
  
  void _navigateToAddTask() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const AddTaskScreen()),
    );
    
    if (result == true) {
      _loadTasks();
    }
  }
  
  void _navigateToTaskDetail(Task task) async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => TaskDetailScreen(task: task),
      ),
    );
    
    if (result == true) {
      _loadTasks();
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildFilterChips(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _loadTasks,
                    child: _filteredTasks.isEmpty
                        ? _buildEmptyState()
                        : ListView.separated(
                            padding: const EdgeInsets.all(AppSizes.paddingMd),
                            itemCount: _filteredTasks.length,
                            separatorBuilder: (context, index) => const SizedBox(height: AppSizes.paddingSm),
                            itemBuilder: (context, index) {
                              final task = _filteredTasks[index];
                              return _buildTaskCard(task);
                            },
                          ),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToAddTask,
        child: const Icon(Icons.add),
      ),
    );
  }
  
  Widget _buildFilterChips() {
    final statuses = ['All', 'To Do', 'In Progress', 'Completed'];
    
    return Container(
      padding: const EdgeInsets.all(AppSizes.paddingMd),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: statuses.map((status) {
            final isSelected = _filterStatus == status;
            return Padding(
              padding: const EdgeInsets.only(right: AppSizes.paddingSm),
              child: FilterChip(
                label: Text(status),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() => _filterStatus = status);
                },
                backgroundColor: AppColors.grey200,
                selectedColor: AppColors.primary.withValues(alpha: 0.2),
                checkmarkColor: AppColors.primary,
                labelStyle: TextStyle(
                  color: isSelected ? AppColors.primary : AppColors.grey700,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
  
  Widget _buildTaskCard(Task task) {
    Color priorityColor = _getPriorityColor(task.priority ?? 'Low');
    Color statusColor = _getStatusColor(task.status ?? 'To Do');
    bool isOverdue = task.dueDate != null && 
                     task.dueDate!.isBefore(DateTime.now()) &&
                     task.status != 'Completed';
    
    return Card(
      child: ListTile(
        leading: Container(
          width: 4,
          decoration: BoxDecoration(
            color: priorityColor,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        title: Row(
          children: [
            Expanded(
              child: Text(
                task.title,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  decoration: task.status == 'Completed' 
                      ? TextDecoration.lineThrough 
                      : null,
                ),
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 6,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: priorityColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                task.priority ?? 'Low',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: priorityColor,
                ),
              ),
            ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (task.description != null)
              Text(
                task.description!,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: AppSizes.fontSm),
              ),
            const SizedBox(height: 4),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 6,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    task.status ?? 'To Do',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: statusColor,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                if (task.dueDate != null)
                  Row(
                    children: [
                      Icon(
                        Icons.calendar_today,
                        size: 12,
                        color: isOverdue ? AppColors.error : AppColors.grey600,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        DateFormatter.formatDate(task.dueDate!),
                        style: TextStyle(
                          fontSize: 10,
                          color: isOverdue ? AppColors.error : AppColors.grey600,
                          fontWeight: isOverdue ? FontWeight.w600 : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
              ],
            ),
            if (task.contactName != null)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Row(
                  children: [
                    const Icon(Icons.person, size: 12, color: AppColors.grey600),
                    const SizedBox(width: 4),
                    Text(
                      task.contactName!,
                      style: TextStyle(
                        fontSize: 10,
                        color: AppColors.grey600,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
        isThreeLine: true,
        onTap: () => _navigateToTaskDetail(task),
      ),
    );
  }
  
  Color _getPriorityColor(String priority) {
    switch (priority.toLowerCase()) {
      case 'urgent':
        return AppColors.error;
      case 'high':
        return AppColors.warning;
      case 'medium':
        return AppColors.info;
      case 'low':
        return AppColors.grey500;
      default:
        return AppColors.grey500;
    }
  }
  
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'to do':
        return AppColors.primary;
      case 'in progress':
        return AppColors.warning;
      case 'completed':
        return AppColors.success;
      case 'cancelled':
        return AppColors.error;
      default:
        return AppColors.grey500;
    }
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.task_outlined,
            size: 80,
            color: AppColors.grey400,
          ),
          const SizedBox(height: AppSizes.paddingMd),
          Text(
            _filterStatus == 'All' ? 'No tasks yet' : 'No $_filterStatus tasks',
            style: const TextStyle(
              fontSize: AppSizes.fontLg,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: AppSizes.paddingSm),
          Text(
            'Create tasks to stay organized',
            style: TextStyle(
              fontSize: AppSizes.fontMd,
              color: AppColors.grey600,
            ),
          ),
        ],
      ),
    );
  }
}
