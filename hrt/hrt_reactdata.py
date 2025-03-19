from db.storage_sqlite import Storage  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_reactvar import HrtReactiveVariable
import pandas as pd
class HrtReactDataFrame():
    def __init__(self):
        # super().__init__('db/dados.xlsx')  # 🔥 Chama o construtor da classe Pai quando xlsx
        # Criando a máscara
        self._hrt_storage = Storage('banco.db', 'hrt_tabela') # 🔥 Chama o construtor da classe Pai quando sqlite
        self._createDataFrame()

    def connectUpdateState(self, updateFunc):
        self._hrt_storage.updateState.connect(updateFunc)

    def disconnectUpdateState(self, updateFunc):
        self._hrt_storage.updateState.disconnect(updateFunc)

    def _createDataFrame(self):
        # Criando o DataFrame com valores None
        self.df = pd.DataFrame(index=self._hrt_storage.df.index, columns=self._hrt_storage.df.columns, dtype=object) 
        for row in self.df.index.to_list():
            for col in self.df.columns.to_list():
                self.df.loc[row, col] = HrtReactiveVariable(row, col, self._hrt_storage)
        

       
    