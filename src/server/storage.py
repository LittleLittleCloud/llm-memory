import os

class Storage:
    def save(self, filename, data):
        '''
        Save or update a file
        '''
        pass
    
    def delete(self, filename):
        '''
        Delete a file
        '''
        pass

    def load(self, filename)->bytes:
        '''
        Load a file
        '''
        pass

    def list(self)->list[str]:
        '''
        List all files
        '''
        pass


class LocalStorage(Storage):
    def __init__(self, root):
        if not os.path.exists(root):
            os.makedirs(root)
        self.root = root

    def save(self, filename, data):
        with open(os.path.join(self.root, filename), 'wb') as f:
            f.write(data)

    def delete(self, filename):
        os.remove(os.path.join(self.root, filename))

    def load(self, filename):
        with open(os.path.join(self.root, filename), 'rb') as f:
            return f.read()

    def list(self):
        return os.listdir(self.root)
    