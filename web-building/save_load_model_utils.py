# ***** UTILS FOR SAVING AND LOADING THE TRAINED MODEL *****

# Save fitted model to a .sav file
def save_model(clf):
    filename = 'trained_model.sav'
    joblib.dump(clf, filename)
    return filename

# Load the fitted model from a .sav file
def load_model(filename):
    return joblib.load(filename)
