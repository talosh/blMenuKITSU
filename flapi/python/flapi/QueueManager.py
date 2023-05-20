from . import Library, Interface, FLAPIException
import json

# QueueManager
#
# Interface for managing the Queue on a Baselight/Daylight system
#

class QueueManager(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a QueueManager object to examine and manipulate the queue on the given zone
    #
    # Arguments:
    #    'zone' (string): Zone name of machine running queue
    #
    # Returns:
    #    (QueueManager): 
    #
    def create(self, zone):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of QueueManager" )
        return self.conn.call(
            None,
            "QueueManager.create",
            {
                'zone': zone,
            }
        )

    # create_local
    #
    # Create a QueueManager object to examine and manipulate the queue on the local zone
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (QueueManager): 
    #
    def create_local(self):
        if self.target != None:
            raise FLAPIException( "Static method create_local called on instance of QueueManager" )
        return self.conn.call(
            None,
            "QueueManager.create_local",
            {}
        )

    # create_no_database
    #
    # Create a QueueManager object to examine and manipulate a non-database queue in the FLAPI process. In addition, the QueueManager object will process any operations added to the queue within the FLAPI process.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (QueueManager): 
    #
    def create_no_database(self):
        if self.target != None:
            raise FLAPIException( "Static method create_no_database called on instance of QueueManager" )
        return self.conn.call(
            None,
            "QueueManager.create_no_database",
            {}
        )

    # get_queue_zones
    #
    # Return list of available zones running queue services
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of strings identifying zones available for rendering
    #        '<n>' (string): Zone name
    #
    def get_queue_zones(self):
        if self.target != None:
            raise FLAPIException( "Static method get_queue_zones called on instance of QueueManager" )
        return self.conn.call(
            None,
            "QueueManager.get_queue_zones",
            {}
        )

    # get_operation_ids
    #
    # Return list operation IDs in queue
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of Operation IDs
    #        '<n>' (int): Operation ID
    #
    def get_operation_ids(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.get_operation_ids",
            {}
        )

    # get_operation
    #
    # Return definition of given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (QueueOp): 
    #
    def get_operation(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.get_operation",
            {
                'id': id,
            }
        )

    # get_operation_status
    #
    # Return status of given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (QueueOpStatus): 
    #
    def get_operation_status(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.get_operation_status",
            {
                'id': id,
            }
        )

    # get_operation_log
    #
    # Return log for given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (list): Array of Log Entries
    #        '<n>' (QueueLogItem): 
    #
    def get_operation_log(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.get_operation_log",
            {
                'id': id,
            }
        )

    # pause_operation
    #
    # Pause operation with given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (none)
    #
    def pause_operation(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.pause_operation",
            {
                'id': id,
            }
        )

    # resume_operation
    #
    # Resume operation with given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (none)
    #
    def resume_operation(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.resume_operation",
            {
                'id': id,
            }
        )

    # restart_operation
    #
    # Restart operation with given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (none)
    #
    def restart_operation(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.restart_operation",
            {
                'id': id,
            }
        )

    # delete_operation
    #
    # Delete operation with given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (none)
    #
    def delete_operation(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.delete_operation",
            {
                'id': id,
            }
        )

    # archive_operation
    #
    # Archive operation with given operation ID
    #
    # Arguments:
    #    'id' (int): Operation ID
    #
    # Returns:
    #    (none)
    #
    def archive_operation(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.archive_operation",
            {
                'id': id,
            }
        )

    # enable_updates
    #
    # Enable status update signals
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def enable_updates(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.enable_updates",
            {}
        )

    # disable_updates
    #
    # Disable status update signals
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def disable_updates(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.disable_updates",
            {}
        )

    # new_operation
    #
    # Create a new custom operation and return its ID
    #
    # Arguments:
    #    'opType' (string): Key identifying the operation type
    #    'desc' (string): Description of operation to present in queue
    #    'params' (dict): Parameters for operation. May contain any simple key/value parameters.
    #    'tasks' (list): Array of tasks for this operation. If you wish to add more tasks to the operation, leave this parameter empty and use add_tasks_to_operation() instead, followed by set_operation_ready(). [Optional]
    #        '<n>' (QueueOpTask): 
    #    'dependsOn' (set): Set of operation IDs that this operation depends on [Optional]
    #
    # Returns:
    #    (int): Operation ID
    #
    def new_operation(self, opType, desc, params, tasks = None, dependsOn = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.new_operation",
            {
                'opType': opType,
                'desc': desc,
                'params': params,
                'tasks': tasks,
                'dependsOn': dependsOn,
            }
        )

    # add_tasks_to_operation
    #
    # Add more tasks to the given operation
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #    'tasks' (list): Array of tasks for this operation
    #        '<n>' (QueueOpTask): 
    #
    # Returns:
    #    (none)
    #
    def add_tasks_to_operation(self, opid, tasks):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.add_tasks_to_operation",
            {
                'opid': opid,
                'tasks': tasks,
            }
        )

    # set_operation_ready
    #
    # Mark operation as ready to process. Should be called after calling add_tasks_to_operation().
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #
    # Returns:
    #    (none)
    #
    def set_operation_ready(self, opid):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.set_operation_ready",
            {
                'opid': opid,
            }
        )

    # get_next_operation_of_type
    #
    # Find the next operation for the given operation type that is ready to execute
    #
    # Arguments:
    #    'opType' (string): Key identifying operation type
    #    'wait' (int): Flag indicating whether the method should block until a task is available
    #
    # Returns:
    #    (int): Operation ID
    #
    def get_next_operation_of_type(self, opType, wait):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.get_next_operation_of_type",
            {
                'opType': opType,
                'wait': wait,
            }
        )

    # get_operation_params
    #
    # Get params for given operation ID
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #
    # Returns:
    #    (dict): 
    #
    def get_operation_params(self, opid):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.get_operation_params",
            {
                'opid': opid,
            }
        )

    # get_next_task
    #
    # Get the next task ready to execute for the given operation ID
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #
    # Returns:
    #    (QueueOpTask): Description of task to execute
    #
    def get_next_task(self, opid):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.get_next_task",
            {
                'opid': opid,
            }
        )

    # set_task_progress
    #
    # Set task progress
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #    'taskseq' (int): Task Sequence Number
    #    'progress' (float): Task progress between 0.0 and 1.0
    #
    # Returns:
    #    (none)
    #
    def set_task_progress(self, opid, taskseq, progress):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.set_task_progress",
            {
                'opid': opid,
                'taskseq': taskseq,
                'progress': progress,
            }
        )

    # set_task_done
    #
    # Mark task as completed
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #    'taskseq' (int): Task Sequence ID
    #    'msg' (string): Task Message
    #
    # Returns:
    #    (none)
    #
    def set_task_done(self, opid, taskseq, msg):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.set_task_done",
            {
                'opid': opid,
                'taskseq': taskseq,
                'msg': msg,
            }
        )

    # set_task_failed
    #
    # Mark task as failed
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #    'taskseq' (int): Task Sequence ID
    #    'msg' (string): Task Message
    #    'detail' (string): Detailed information on failure
    #    'frame' (int): Frame number of failure [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_task_failed(self, opid, taskseq, msg, detail, frame = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.set_task_failed",
            {
                'opid': opid,
                'taskseq': taskseq,
                'msg': msg,
                'detail': detail,
                'frame': frame,
            }
        )

    # add_operation_log
    #
    # Add log entry for operation
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #    'type' (string): Type of log entry
    #    'msg' (string): Log Message
    #    'detail' (string): Detailed information on failure
    #
    # Returns:
    #    (none)
    #
    def add_operation_log(self, opid, type, msg, detail):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.add_operation_log",
            {
                'opid': opid,
                'type': type,
                'msg': msg,
                'detail': detail,
            }
        )

    # add_task_log
    #
    # Add log entry for operation
    #
    # Arguments:
    #    'opid' (int): Operation ID
    #    'taskseq' (int): Task Sequence ID
    #    'type' (string): Type of log entry
    #    'msg' (string): Log Message
    #    'detail' (string): Detailed information on failure
    #    'frame' (int): Frame number within task for log entry [Optional]
    #
    # Returns:
    #    (none)
    #
    def add_task_log(self, opid, taskseq, type, msg, detail, frame = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "QueueManager.add_task_log",
            {
                'opid': opid,
                'taskseq': taskseq,
                'type': type,
                'msg': msg,
                'detail': detail,
                'frame': frame,
            }
        )

Library.register_class( 'QueueManager', QueueManager )

