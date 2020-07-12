import programenv as pe
import sys


from functools import partial

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTabWidget, QVBoxLayout, QPushButton, QTreeView, QTreeWidget, QTreeWidgetItem, QSystemTrayIcon, QMenu
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt

class GUI(QWidget):
    def __init__(self, app=None):
        self.QApp = QApplication([]) # Before super().__init__() because QWidget.__init__() requires a QApplication already running!
        super().__init__()
        self.app = app
        self.width = 480
        self.height = 320
        
    def initUI(self):
        self.setWindowTitle(pe.PROGRAMNAME + ' ' + pe.VERSION)
        self.setGeometry(50,50,self.width,self.height) # TODO Change this to something relative to screen size

        
        ## Create main window
        # Create tabs
        self.tabs = QTabWidget()
        self.tab1, self.tab2 = QWidget(), QWidget()
        self.tabs.resize(self.width, self.height)
        
        self.tabs.addTab(self.tab1, "Options")
        #self.tabs.addTab(self.tab2, "Tab 2")

        ## Layout main window
        self.grid = QGridLayout()
        self.grid.addWidget(self.tabs)
        self.setLayout(self.grid)
        

        ## Create first tab
        self.tab1_treeView = RocketTreeWidget(self.readRockets())
        self.tab1_treeView.itemChanged.connect(lambda item, column: self.activateConfirmationButton(activate=True))
        self.tab1_confirmButton = QPushButton(self)
        self.tab1_confirmButton.setText("Confirm")
        self.tab1_confirmButton.clicked.connect(self.confirmSettings)

        ## Layout first tab
        self.tab1.layout = QGridLayout()
        self.tab1.layout.addWidget(self.tab1_treeView, 1, 0, 1, 2)
        self.tab1.layout.addWidget(self.tab1_confirmButton, 2, 0, 1, 2)
        self.tab1.setLayout(self.tab1.layout)


        self.show()
        self.QApp.exec_()
    
    def readRockets(self, path='data/rockets.csv'):
        '''
            @param path (str): 
            @return (dict): Tree with country -> provider -> family
        '''
        # Return nested dictionary of rockets, I guess
        with open(path) as inFile:
            data = [[field.strip() for field in line.strip().split(',')] for line in inFile][1:]
        
        blockedRockets = self.app.options.get('blockedRockets')

        tree = {}
        for rocket in data:
            status = rocket[2]
            if status not in ['Active', 'Development']: # If the rocket is no longer in use, don't bother
                continue
            family = rocket[1]
            provider = rocket[3]
            country = rocket[4]
            if country not in tree: # If country not encountered yet, add it to dictionary
                tree[country] = {}
            if provider not in tree[country]: # If provider not encountered yet...
                tree[country][provider] = {}
            tree[country][provider][family] = family not in blockedRockets
        
        return tree
    
    def confirmSettings(self):
        blockedRockets = []
        for family, item in self.tab1_treeView.treeWidgets['family'].items():
            if item.checkState(0) == Qt.Unchecked:
                blockedRockets.append(family)
        
        self.app.options.set('blockedRockets', blockedRockets, saveFile=True)
        self.activateConfirmationButton(False)
    
    def activateConfirmationButton(self, activate=True):
        self.tab1_confirmButton.setEnabled(activate)


class RocketTreeWidget(QTreeWidget):
    def __init__(self, tree):
        super().__init__()
        self.setHeaderHidden(True) # Could use setHeaderLabels if columns are desired
        self.setAnimated(True)

        self.treeWidgets = {'root': None, 'country': {}, 'provider': {}, 'family': {}}
        self.rocketTree = tree

        rootItem = RocketTreeItem(self, 'All', 'root')
        self.treeWidgets['root'] = rootItem
        rootItem.setExpanded(True)
        for country, providers in self.rocketTree.items():
            countryItem = RocketTreeItem(rootItem, country, 'country')
            self.treeWidgets['country'][country] = countryItem
            for provider, families in providers.items():
                providerItem = RocketTreeItem(countryItem, provider, 'provider')
                self.treeWidgets['provider'][provider] = providerItem
                for family, allowed in families.items():
                    familyItem = RocketTreeItem(providerItem, family, 'family')
                    self.treeWidgets['family'][family] = familyItem
                    familyItem.setCheckState(0, Qt.Checked if allowed else Qt.Unchecked)
        
        # self.expandAll()
        self.sortItems(0, Qt.SortOrder(Qt.AscendingOrder))
    

class RocketTreeItem(QTreeWidgetItem):
    def __init__(self, parent, text, itemType):
        super().__init__(parent)
        self.setText(0, text)

        if itemType == 'root':
            fontSize, bold, color = 10, False, QColor(0, 0, 0)
            self.setFlags(self.flags() | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable)
        elif itemType == 'country':
            fontSize, bold, color = 10, False, QColor(0, 0, 0)
            self.setFlags(self.flags() | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable)
        elif itemType == 'provider':
            fontSize, bold, color = 10, False, QColor(0, 0, 0)
            self.setFlags(self.flags() | Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable)
        elif itemType == 'family':
            fontSize, bold, color = 10, False, QColor(0, 0, 0)
            self.setFlags(self.flags() | Qt.ItemIsUserCheckable)

        fnt = QFont('Arial', fontSize)
        fnt.setBold(bold)
        self.setFont(0, fnt)
        self.setForeground(0, color)


# TODO: Problem with tray icon is that it dies when the main window is closed with X or something else, so need to bind it to something else?
# class TrayIcon(QSystemTrayIcon):
#     def __init__(self, iconPath, app=None):
#         super().__init__(QIcon(iconPath))
#         self.app = app
#         menu = QMenu()
#         exitAction = menu.addAction("Exit")
#         exitAction.triggered.connect(self.app.close)
#         self.setContextMenu(menu)


if __name__ == '__main__':
    from main import App
    app = App()
    x = GUI(app)
    x.initUI()