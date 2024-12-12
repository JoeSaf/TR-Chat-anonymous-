def home_logo():
    print(r"""
                 _     _   ___ _                ___       
                | |   | | /   | |              /   |      
                | |__ | |/ /| | | ___ __ ___  / /| |_ __  
                | '_ \| / /_| | |/ / '_ ` _ \/ /_| | '_ \ 
                | |_) | \___  |   <| | | | | \___  | | | |
                |_.__/|_|   |_/_|\_\_| |_| |_|   |_/_| |_|
                                          
                                          
    
bl4k4n: The quieter you become, the more you'll hear
    """)

def Main():
    home_logo()
    print("1\tStart Server\n2\tConnect with server")
    print("Once inside a server type 'BYE' to leave")
    print("Don't be a smartass, yes type 'BYE' in capital to leave,\nIm not dumb to tell you so")
    select = int(input("Select ::: "))
    if select == 1:
        import server
    elif select == 2:
        import client
    else:
        print("Please choose 1 or 2")

if __name__ == "__main__":
    Main()
