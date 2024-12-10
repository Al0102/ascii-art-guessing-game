'''
import_image(file, height, start, do_colour)
    Imports the image from a text file
    
    return (string)
      - Returns "ascii image" from text file as a string
     
    Parameters:
        file (string)
          - File path of text file holding the ascii image
          - e.g. "foo.txt"
        height (int)
          - Height of ascii image (number of lines in file)
        start (int)
          - default: 0
          - The first line in file to start taking in input
        do_colour (bool)
          - default: False
          - If set to True, uses the next {height} lines
            after the ascii image in the file as the "bitmap"
            argument when it calls: merge_ascii_colourmap()
    
'''
def import_image(file, height, start=0, do_colour=False):
    with open (file, 'r', encoding='utf-8') as f:
        file = f.readlines()
        img = ''.join(file[start:start+height])
        if do_colour:
            colourmap = ''.join(file[start+height:start+2*height])
            return merge_ascii_colourmap(img, colourmap)
        else:
            img = '\033[0m'+img
        return img

'''
merge_ascii_colourmap(image, bitmap)
    Combines an ASCII image with its corresponding colourmap
    
    return (string)
      - Returns a new ascii image
        with the corresponding ANSI escape codes inserted
      - newlines (\n) used to separate lines 

    Parameters:
        image (string or 2D list)
          - The ascii image
        bitmap (bitmap style string of digits 0-9 or spaces)
          - Map of colours corresponding to the ascii image
            0 - Black
            1 - Red
            2 - Green
            3 - Yellow
            4 - Blue
            5 - Magenta
            6 - Cyan
            7 - White
            8 - Grey (faint white)
            9 - Bold white
'''
def merge_ascii_colourmap(image, bitmap):
    if type(image) == str:
        new_image = list(map(list, image.split('\n')))
    else:
        new_image = image[:]
    if type(bitmap) == str:
        bitmap_f = bitmap.split('\n')

    for line in range(len(bitmap_f)):
        temp_line = bitmap_f[line]

        while len(temp_line) > 0:
            temp_char = temp_line[-1]
            if temp_char == '8':
                colour_value = '2'
            elif temp_char == '9':
                colour_value = '1'
            else:
                colour_value = '3'+temp_char

            temp_line = temp_line.rstrip(temp_char)
            new_image[line].insert(
                    len(temp_line),
                        f"\033[0m\033[{colour_value}m")
        new_image[line].append("\033[0m")

    new_image = '\n'.join(map(lambda x: ''.join(x), new_image))
    return new_image

def main():
    import time
    import random
    import os

    IMAGES = (
              {"answer": "happymeal",
               "image":import_image("images.txt", 7, do_colour=True),
               "hint":"McDonald's meal for kids"},
              {"answer": ("casket","coffin"),
               "image":import_image("images.txt", 14, start=14, do_colour=True),
               "hint": "What you put dead people in"},
              {"answer":("sock","stocking"),
               "image":import_image("images.txt", 13, start=42, do_colour=True),
               "hint":"Foot warmers"},
              {"answer": "fox",
               "image":import_image("images.txt", 8, start=68, do_colour=True),
               "hint": "What does the ___ say?"},
              {"answer": "pirateship",
               "image":import_image("images.txt", 32, start=162, do_colour=True),
               "hint": "Arr matey, let's hit the high seas and get some booty"},
              {"answer": "golf",
               "image": import_image("images.txt", 18, start=126, do_colour=True),
               "hint": "Hole in one!"},
              )

    try:
        with open("high-score.txt", 'r') as f:
            high_score=int(f.readline().strip('\n '))
            high_score_time=float(f.readline().strip('\n '))
    except (FileNotFoundError, ValueError):
        with open("high-score.txt", 'w') as f:
            f.write("0\n0\n")
            high_score = 0
            high_score_time = 0
        print("Creating new file 'high-score.txt'...")
        time.sleep(1)

    while True:
        # Initialize game
        remaining_questions = random.sample(IMAGES,len(IMAGES))
        points = 0
        POINT_PAYOUT = (5,2,1)
        total_time = 0
        finish_time = 0

        if not high_score:
            input("\033[2J\033[1;1H"+
              f"""
              Welcome to ASCII Art Guesser!

              After beginning the game, a series of {len(IMAGES)} different images will be shown.
              Type in what you think each image is then click \033[1m\033[33m[ENTER]\033[0m

              You will have three guesses per image
              Succeeding on the first try awards {POINT_PAYOUT[0]} points, second try {POINT_PAYOUT[1]} points, and third try {POINT_PAYOUT[2]} point.
              Additionally, bonus points may be awarded for speedy answers.

              < Art by Alex Lu >

              Press \033[1m\033[93m[ENTER]\033[0m when you are \033[1m\033[32mREADY\033[0m
              """)
        else:
            input("\033[2J\033[1;1H"+
                    f"High score: {high_score}\nTime: {high_score_time:.2f}\n\nPress \033[1m\033[93m[ENTER]\033[0m when you are \033[1m\033[32mREADY\033[0m")

        # Start game
        for question in remaining_questions:
            # Clear screen then print image
            print("\033[2J\033[H" +
                  question["image"]+'\n')

            start_time = time.time()
            guess = None

            # 3 Guesses
            for i in range(3):
                print(f"\033[2K{3-i} tries left"+('\n' if not guess else ''))
                if guess:
                    print("\033[2KPrevious Guess: "+guess)
                guess = input("\033[2K> ").replace(" ", "").lower()
                
                # Prevents window scrolling - resulting in image disappearing as guesses are made
                scrollup = "\033[1T\033[3A" if len(question["image"].split('\n')) > os.get_terminal_size()[1]-4 else "\033[4A"
                print(f"{scrollup}", end='')

                # Answer check
                if guess == question["answer"] or (guess in question["answer"] and type(question["answer"])==tuple):
                    finish_time = time.time()
                    points += POINT_PAYOUT[i]
                    points += max(5-int(finish_time-start_time), 0)
                    break

                # Print hint
                print("Hint: "+question["hint"])

            # Spacing
            print("\n\n\n")
            # Time and correct answers for too many incorrect guesses
            if finish_time < start_time:
                finish_time = time.time()
                print("Incorrect\nAnswer(s): ",str(question["answer"]).strip("()"))

            total_time += finish_time-start_time
            input(f"Time: {(finish_time-start_time):.2f}\nPoints: {points}\n\n\033[1m\033[93m[ENTER]\033[0m")

        # Game end
        if points >= high_score:
            high_score = points 
            if total_time < high_score_time:
                high_score_time = total_time
        print("\033[2J\033[1;1H")
        print(f"\033[33mFinal Score: {points}\nFinal Time: {total_time:.2f}\033[0m\n")

        while restart:=(input("Play again?\n(y)es | (n)o\n").lower().strip()+'_')[0]:
            if restart == 'y':
                break
            elif restart == 'n':
                with open("high-score.txt", 'w') as f:
                    f.write(str(high_score)+'\n')
                    f.write(f"{high_score_time:.2f}")

                return


if __name__ == "__main__":
    # Saves current screen and hides cursor
    print("\033[2J\033[1;1H\033[?25l\033[?1049h", end='')

    main()

    # Returns screen to original after game is done
    print("\033[2J\033[?25h\033[?1049;1l", end='')
