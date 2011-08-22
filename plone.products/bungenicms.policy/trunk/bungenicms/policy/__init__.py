from transaction._transaction import Savepoint
from transaction._transaction import NoRollbackSavepoint

def __init__(self, transaction, optimistic, *resources):
    self.transaction = transaction
    self._savepoints = savepoints = []
    
    for datamanager in resources:
        try:
            savepoint = datamanager.savepoint
        except AttributeError:
            if not optimistic:
                pass
            savepoint = NoRollbackSavepoint(datamanager)
        else:
                savepoint = savepoint()
                
        savepoints.append(savepoint)
Savepoint.__init__ = __init__
                
def rollback(self):
    pass    
NoRollbackSavepoint.rollback = rollback
