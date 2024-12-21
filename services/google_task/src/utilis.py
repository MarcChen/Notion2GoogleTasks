import os 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def save_hyperparameters(args, output_dir):
    """Save hyperparameters to a text file."""
    hyperparams_path = os.path.join(output_dir, "hyperparameters.txt")
    with open(hyperparams_path, "w") as f:
        for arg in vars(args):
            f.write(f"{arg}: {getattr(args, arg)}\n")
    print(f"Hyperparameters saved at: {hyperparams_path}")

def colored_print(color, text):
    """
    Print text with the specified color and reset to default color at the end.
    Args:
        color (str): The color code from the bcolors class.
        text (str): The text to print.
    """
    print(f"{color}{text}{bcolors.ENDC}")