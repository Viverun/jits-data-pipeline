import shutil
from .runner import BaseStep

class ConsolidationStep(BaseStep):
    def process_item(self, data):
        # BaseStep handles reading and writing.
        # For consolidation, we just return the data as is.
        return data

    def run(self):
        # Override run if we want to also copy files instead of just reading/writing JSON
        # effectively BaseStep already does what step08 does (reads from input_dir, writes to output_dir)
        super().run()
