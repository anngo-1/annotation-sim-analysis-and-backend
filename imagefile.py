
class ImageFile:
    def __init__(self, name, df):
        self.name = name
        self.df = df
        self.total_agreement = None
        self.per_tag_agreement = None

    def __str__(self):
        return "Name: " + self.name + "\nDataFrame:\n" + str(self.df) + "\nTotal Agreement: " + str(self.total_agreement) + "Agreement Per Tag: " + str(self.per_tag_agreement)
