import os

class Storage:
    async def save(self, filename, data):
        '''
        Save or update a file
        '''
        pass
    
    async def delete(self, filename):
        '''
        Delete a file
        '''
        pass

    async def load(self, filename)->bytes:
        '''
        Load a file
        '''
        pass

    async def list(self)->list[str]:
        '''
        List all files
        '''
        pass


class LocalStorage(Storage):
    def __init__(self, root):
        if not os.path.exists(root):
            os.makedirs(root)
        self.root = root

    async def save(self, filename, data):
        with open(os.path.join(self.root, filename), 'wb') as f:
            f.write(data)

    async def delete(self, filename):
        os.remove(os.path.join(self.root, filename))

    async def load(self, filename):
        with open(os.path.join(self.root, filename), 'rb') as f:
            return f.read()

    async def list(self):
        return os.listdir(self.root)
    