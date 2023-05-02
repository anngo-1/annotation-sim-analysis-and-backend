
class ImageFile:
    def __init__(self, name, all_tags_df):
        self.name = name
        self.all_tags_df = all_tags_df
        self.agreement_df = None
        self.total_agreement = 0

    def __str__(self):
        return "Name: " + self.name + "\nDataFrame:\n" + str(self.all_tags_df) 

    def print_agreement(self):
        return "File: " + self.name + "\nAgreement:\n" + str(self.agreement_df) + "\nTotal Agreement: " + str(self.total_agreement) + "\n\n"