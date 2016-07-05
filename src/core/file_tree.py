"""
A very simplified Tree-like structure, which represents the "inner" filesystem
of a torrent file. According to the BitTorrent protocol, this filesystem is
composed from either only one file or many files within a root directory.
For example:
    - A torrent which contains the file FILE1
    - A torrent which contains more files, but all of them are automatically
    put in a root directory : ROOT/FILE1, ROOT/DIR1/FILE2 and so on..
When adding a file, the path must be absolute and must start with the
root directory. For example:

Suppose, that the root directory is TorrentFolder.
The paths to the files, which are to be added must look like this:
    - TorrentFolder/file1
    - TorrentFolder/dir1/file2
    - ... and so on.

If the torrent contains only one file, it should be added in the tree when
initialized, with other words - the filename must be passed to the __init__
method of FileTree.
"""


class TreeNode:
    def __init__(self, path, size=0):
        self.path = path
        self.size = size
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    # Get the child with the given value
    # Returns TreeNode if the child is present, None otherwise
    def __getitem__(self, path):
        for child in self.children:
            if child.path == path:
                return child

        return None

    def is_leaf(self):
        return len(self.children) == 0


class FileTree:
    def __init__(self, value, size=0):
        self.root = TreeNode(value, size)

    def add_file(self, path, size):
        if '/' not in path:
            return

        parts = path.split('/')[1:]
        self.add_recursively(self.root, parts, size)

    def add_recursively(self, node, dirs, size):
        if len(dirs) == 1:
            node.add_child(TreeNode(dirs[0], size))
        else:
            child = node[dirs[0]]
            if not child:
                node.add_child(TreeNode(dirs[0]))
                child = node[dirs[0]]

            self.add_recursively(child, dirs[1:], size)

    def get_root(self):
        return self.root
