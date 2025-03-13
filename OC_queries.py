from flask import Flask, jsonify

app = Flask(__name__)

OPENCITATION_META_API_URL = "https://opencitations.net/meta/api/v1/metadata/"
selected_papers= "C:\Users\franc\OneDrive - Alma Mater Studiorum Università di Bologna\Desktop\IRCDL\data\IRCDL - paper resource selection  - Selected resources.csv"


def doi_OpenCitation_META_info(doi):
    """Get info for DOI in OpenCitation Meta."""

    return True 

def doi_OpenCitation_index_info(doi):
    """Get info for DOI in OpenCitation Index."""

    return True



if __name__ == '__main__':
    app.run(debug=True)