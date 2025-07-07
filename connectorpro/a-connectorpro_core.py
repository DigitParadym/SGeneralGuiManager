
import os
import csv
import shutil
import logging

class ConnectorPro:
    def __init__(self, config):
        self.config = config
        self.source_folder = self.config['source_folder']
        self.destination_folder = self.config['destination_folder']
        self.data_file = os.path.join(os.path.dirname(__file__), 'data', 'connectorpro_actions.csv')
        logging.basicConfig(filename='connectorpro_core.log', level=logging.INFO)

    def move_file_with_versioning(self, source_path):
        """Move the file to the destination folder, appending a version if needed."""
        base_name = os.path.basename(source_path)
        destination_path = os.path.join(self.destination_folder, base_name)
        shutil.move(source_path, destination_path)
        logging.info(f"Moved {source_path} to {destination_path}")
        return destination_path

    def process_and_move_files(self, file_pattern="*.py"):
        """Process files, move them, and log only names and paths to CSV."""
        # Step 1: Delete old CSV if it exists
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
            logging.info("Deleted old CSV file")

        moved_files = []

        # Step 2: Process each file in the source folder
        for filename in os.listdir(self.source_folder):
            if filename.endswith('.py'):  # Adjust pattern as needed
                source_path = os.path.join(self.source_folder, filename)
                new_path = self.move_file_with_versioning(source_path)
                moved_files.append((filename, new_path))

        # Step 3: Write new CSV with only names and paths of moved files
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['File Name', 'Path'])  # Write header
                writer.writerows(moved_files)           # Write file data
            logging.info(f"CSV updated with {len(moved_files)} records")
        except Exception as e:
            logging.error(f"Error creating CSV: {e}")

        return moved_files
