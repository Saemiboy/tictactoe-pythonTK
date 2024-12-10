import tkinter as tk
from tkinter import font
from tkinter import colorchooser
import os
import pygame

# Globals
board = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]
player = 1
size = 540
feldgroesse = size//3
spielerXStand = 0
spielerOStand = 0
remainingTime = 2
afterID = None # Für Countdown

# Colorpalette
dark = '#003B46'
middark = '#07575B'
fontcol = '#C4DFE6'
between = '#66A5AD'
winnerlinecol = dark
xCol = '#FB6542'
oCol = '#FFBB00'
bgColor = '#66A5AD'

##################################################### Funktionien #################################################

def initializeGame():
    # zeichnet die Linien
    for ver in range(1,3):
        canvas.create_line(ver*feldgroesse, 0, ver*feldgroesse, size, width=3, fill=fontcol)
    for hor in range(1,3):
        canvas.create_line(0, hor*feldgroesse, size, hor*feldgroesse, width=3, fill=fontcol)

def checkEmpty(grid):
    for row in grid:
        for element in row:
            if element == 0:
                return True
    return False

def findFeld(mouse):
    global feldgroesse
    # Berechnung in welchem Feld geckilckt wurde
    feldx, feldy = mouse.x//feldgroesse, mouse.y//feldgroesse
    return (feldx, feldy)

def feldBesetzt(coords):
    global board
    if board[coords[1]][coords[0]] != 0:
        return True
    else:
        return False

def drawMove(coords):
    global feldgroesse, player, board
    if player == 1:
        # zeichnet ein Kreuz
        canvas.create_line((coords[0]*feldgroesse)+20, (coords[1]*feldgroesse)+20, ((coords[0]+1)*feldgroesse) - 20, ((coords[1]+1)*feldgroesse) - 20, width=5, fill=xCol)
        canvas.create_line((coords[0]*feldgroesse)+20, ((coords[1]+1)*feldgroesse)-20, ((coords[0]+1)*feldgroesse) - 20, (coords[1]*feldgroesse) + 20, width=5, fill=xCol)
        board[coords[1]][coords[0]] = 1
        playSound('click')
    else:
        # zeichnet ein Kreis
        canvas.create_oval((coords[0]*feldgroesse)+20, (coords[1]*feldgroesse)+20, ((coords[0]+1)*feldgroesse) - 20, ((coords[1]+1)*feldgroesse) - 20, width=5, outline=oCol)
        board[coords[1]][coords[0]] = 2
        playSound('click')

def check_all_equal(l):
    for li in l:
        # drei 0s sollten kein gewinn kreieren
        if len(set(li)) == 1 and 0 not in li:
            return (True, l.index(li))
    return (False, l.index(li))

def drawWinLine(art, pos):
    global feldgroesse
    if art == 'row':
        canvas.create_line(feldgroesse/2 - 50, (pos*feldgroesse) + (feldgroesse/2), size - (feldgroesse/2 - 50), (pos*feldgroesse) + (feldgroesse/2), width=10, fill=winnerlinecol)
    elif art == 'col':
        canvas.create_line((pos*feldgroesse) + (feldgroesse/2), feldgroesse/2 - 50, (pos*feldgroesse) + (feldgroesse/2) , size - (feldgroesse/2 - 50), width=10, fill=winnerlinecol)
    elif art == 'dia':
        if pos == 1:
            canvas.create_line(50, size-50, size-50, 50, width=10, fill=winnerlinecol)
        else:
            canvas.create_line(50, 50, size-50, size-50, width=10, fill=winnerlinecol)

def checkforWin():
    global board
    rows = board
    cols = [[row[i] for row in board] for i in range(len(board[0]))]
    diags = [[board[i][i] for i in range(len(board))], [board[i][len(board)-1-i] for i in range(len(board))]]
    if check_all_equal(rows)[0]:
        line_pos = check_all_equal(rows)[1]
        drawWinLine('row', line_pos)
        return True
    elif check_all_equal(cols)[0]:
        line_pos = check_all_equal(cols)[1]
        drawWinLine('col', line_pos)
        return True
    elif check_all_equal(diags)[0]:
        line_pos = check_all_equal(diags)[1]
        drawWinLine('dia', line_pos)
        return True
    else:
        return False
    
def schliessen():
    root.destroy()

def restartGame(window):
    global board, player
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    # zerstört das winnerwindoe
    if window:
        window.destroy()
    items = canvas.find_all()
    for item in items:
        canvas.delete(item)
    canvas.bind('<Button-1>', macheSpielzug)
    initializeGame()
    updateAktuellerSpieler()
    playSound('bg')
    restartCountdown()

def changeColor():
    global bgColor
    color_code = colorchooser.askcolor(title='Neue Hintergrundfarbe')
    # schaut ob eine farbe ausgesucht wurde oder nicht
    if color_code:
        bgColor = color_code[1]
        canvas.config(bg=bgColor)

    restartGame(None)

def winnerWindow(spieler):
    global player, afterID

    if afterID is not None:
        root.after_cancel(afterID)
        afterID = None

    # Geometrie des Hauptfensters ermitteln
    main_window_width = root.winfo_width()
    main_window_height = root.winfo_height()
    main_window_x = root.winfo_x()
    main_window_y = root.winfo_y()
    
    # Größe des neuen Fensters definieren
    new_window_width = 300
    new_window_height = 300
    
    # Position des neuen Fensters berechnen
    new_window_x = main_window_x + (main_window_width // 2) - (new_window_width // 2)
    new_window_y = main_window_y + (main_window_height // 2) - (new_window_height // 2)

    new_window = tk.Toplevel(root)
    # positioniert das neue Fenster genau in der Mitte des alten Fensters
    new_window.geometry(f'{new_window_width}x{new_window_height}+{new_window_x}+{new_window_y}')
    new_window.config(bg=middark)

    if spieler == 3:
        win_text = 'Unentschieden'
        playSound('unentschieden')
    else: 
        win_text = 'Gewinner:'
        playSound('win')

    label_win = tk.Label(new_window, text=win_text, font=('Helvetica', '20'), bg=middark, fg=fontcol)
    label_win.pack(anchor=tk.CENTER, pady=10)

    canvas_win = tk.Canvas(new_window, width=50, height=50, bg=middark, highlightthickness=0)
    canvas_win.pack(pady=5, anchor=tk.CENTER)

    # neues Frame für die Buttons die nebeneinander hinkommen
    frame_win = tk.Frame(new_window, bg=middark)
    frame_win.pack(pady=20)

    # exit button
    exit_btn_win = tk.Button(frame_win, text='Exit', width=9, command=schliessen, bg=middark, border=3, fg=fontcol, font=custom_font15)
    exit_btn_win.pack(side=tk.LEFT, padx=10)

    # restart button
    rest_btn_win = tk.Button(frame_win, text='Restart', width=10, command=lambda: restartGame(new_window), bg=middark, border=3, fg=fontcol, font=custom_font15)
    rest_btn_win.pack(side=tk.LEFT, padx=10)

    # color btn
    changeCol_btn = tk.Button(new_window, text='Change Color', width=12, command=changeColor, bg=middark, border=3, fg=fontcol, font=custom_font15)
    changeCol_btn.pack(pady=10)

    if spieler == 1:
        canvas_win.create_line(5, 5, 45, 45, fill=xCol, width=5)
        canvas_win.create_line(5, 45, 45, 5, fill=xCol, width=5)
        updateSpielstand('kreuz')
    elif spieler == 2:
        canvas_win.create_oval(5, 5, 45, 45, outline=oCol, width=5)
        updateSpielstand('kreis')

def spielregelnWindow():
    playSound('intro')
    # Geometrie des Hauptfensters ermitteln
    main_window_width = root.winfo_screenwidth()
    main_window_height = root.winfo_screenheight()
    main_window_x = root.winfo_x()
    main_window_y = root.winfo_y()
    
    # Größe des neuen Fensters definieren
    new_window_width = 600
    new_window_height = 600
    
    # Position des neuen Fensters berechnen
    new_window_x = main_window_x + (main_window_width // 2) - (new_window_width // 2)
    new_window_y = main_window_y + (main_window_height // 2) - (new_window_height // 2)

    spielregel_window = tk.Toplevel(root, bg=middark)
    # positioniert das neue Fenster genau in der Mitte des alten Fensters
    spielregel_window.geometry(f'{new_window_width}x{new_window_height}+{new_window_x}+{new_window_y}')
    spielregel_window.title('Spielregeln')
    spielregel_window.transient(root)  # Bindet das Fenster ans Hauptfenster
    spielregel_window.grab_set() # verhindert interaktion mit hauptfenster wenn das fenster geöffnet ist


    # Titel
    spielregeln_titel = tk.Label(spielregel_window, text='Spielregeln', font=custom_font, bg=middark, fg=fontcol)
    spielregeln_titel.pack(pady=10)

    # regeln hinzufügen
    regeln = [
        '1. Es wird abwechslungsweise Spieler X und Spieler O gespielt',
        '2. Gewinner ist, wer zuerst drei Zeichen in einer Spalte, Reihe oder Diagonale hat',
        '3. Wenn Spiel neugestartet wird, beginnt der Verlierer',
        '4. Bei einem Unentschieden fängt danach der andere Spieler an',
        '5. Wenn der Spielstand zurückgesetzt wird beginnt alles von vorne',
        '6. Für jeden Zug hat der Spieler 2 Sekunden Zeit sonst hat er verloren'
    ]
    
    for punkt in regeln:
        label = tk.Label(spielregel_window, text=punkt, font=custom_font15, wraplength=550, bg=middark, fg=fontcol)
        label.pack(pady=7)

    # schliessen button
    schliessenbutton = tk.Button(spielregel_window, text='START', font=custom_font15, command=spielregel_window.destroy, bg=middark, border=3, fg=fontcol)
    schliessenbutton.pack(pady=10)

    root.wait_window(spielregel_window)

def updateSpielstand(form):
    global spielerXStand, spielerOStand, player
    if form == 'kreuz':
        spielerXStand += 1
        spieler1Label.config(text=f'{spielerXStand}')
        player = 2
    elif form == 'kreis':
        spielerOStand += 1
        spieler2Label.config(text=f'{spielerOStand}')
        player = 1
    else:
        spieler1Label.config(text=f'{spielerXStand}')
        spieler2Label.config(text=f'{spielerOStand}')

def freezeBoard():
    global board
    for row in range(len(board)):
        for col in range(len(board)):
            if board[row][col] == 0:
                board[row][col] = 4
    # macht das das Canvas nicht mehr auf den Mausklick reagiert. Wird dann bei restartGame wieder gebindet
    canvas.unbind('<Button-1>')

def updateAktuellerSpieler():
    global player
    items = spielerCanvas.find_all()
    for item in items:
        spielerCanvas.delete(item)
    if player == 1:
        spielerCanvas.create_line(60, 60, 140, 140, fill=xCol, width=4)
        spielerCanvas.create_line(140, 60, 60, 140, fill=xCol, width=4)
    else:
        spielerCanvas.create_oval(60, 60, 140, 140, outline=oCol, width=4)

def resetSpielstand():
    global spielerXStand, spielerOStand
    spielerOStand, spielerXStand = 0, 0
    updateSpielstand(None)

def macheSpielzug(event):
    global board, player, feldgroesse
    # schaut dass wenn nochmals reingeklickt wird immernoch winnerwin gezeigt wird
    if checkforWin():
        return winnerWindow(player)
    if checkEmpty(board):
        pass
    else:
        # macht auch das neue window einfach als draw
        return winnerWindow(3)
    
    feld = findFeld(event)
    if feldBesetzt(feld):
        return
    else:
        pass

    drawMove(feld)

    if checkforWin():
        freezeBoard()
        return winnerWindow(player)
    else:
        if player == 1:
            player = 2
        elif player == 2:
            player = 1
        updateAktuellerSpieler()

    # braucht es damit direkt erkannt wird ob unentschieden ist und nicht noch mal gedrückt werden muss
    if not checkEmpty(board):
        return winnerWindow(3)
    
    restartCountdown()
    
def playSound(sound):
    if sound == 'bg':
        channel1.play(backgroundSound, loops=-1)
    elif sound == 'click':
        channel2.play(clickSound)
    elif sound == 'win':
        channel1.stop()
        channel3.play(winSound)
    elif sound == 'unentschieden':
        channel1.stop()
        channel3.play(unentschiedenSound)
    elif sound == 'intro':
        channel4.play(intro, loops=-1)

def restartCountdown():
    global remainingTime, afterID
    # muss alten countdown zuerst löschen bevor neuen gemacht wird
    if afterID is not None:
        root.after_cancel(afterID)
        afterID = None
    remainingTime = 2
    countdown.config(text=f'{remainingTime} Sekunden')
    startCountdown()

def timeUp():
    countdown.config(text='Zeit abgelaufen')
    freezeBoard()
    if player == 1:
        winner = 2
    else:
        winner = 1
    return winnerWindow(winner)

def startCountdown():
    global remainingTime, afterID
    if remainingTime >= 0:
        countdown.config(text=f'{remainingTime} Sekunden')
        remainingTime -= 1
        afterID = root.after(1000, startCountdown)
    else:
        timeUp()

############################################## Ganzes Window definieren mit allen widgets ################################

# Window
root = tk.Tk()
root.state('zoomed')
# root.overrideredirect(True)
root.title('Tic Tac Toe')
root.config(bg=dark)

custom_font = font.Font(family="Verdana", size=60, )
custom_font25 = font.Font(family="Verdana", size=25)
custom_font15 = font.Font(family="Verdana", size=15)

# Spieler Text
spielerFrame = tk.Frame(root, height=root.winfo_vrootheight(), bg=dark)
spielerFrame.place(relx=0.7, anchor='nw', relwidth=0.3)
spielerLabel = tk.Label(spielerFrame, text='Aktueller Spieler', font=custom_font25, bg=dark, fg=fontcol)
spielerLabel.place(relx=0.5, rely=0.16, anchor='n')
spielerCanvas = tk.Canvas(spielerFrame, height=200, width=200, bg=dark, highlightthickness=0)
spielerCanvas.place(relx=0.5, rely=0.46, anchor='center')

# Spielstand 
spielstandFrame = tk.Frame(root, height=root.winfo_vrootheight(), bg=dark)
spielstandFrame.place(anchor='nw', relwidth=0.3)
spielstandLabel = tk.Label(spielstandFrame, text='Spielstand', font=custom_font25, bg=dark, fg=fontcol)
spielstandLabel.place(relx=0.5, rely=0.16, anchor='n')
nummerFrame = tk.Frame(spielstandFrame, width=350, height=250, bg=dark)
nummerFrame.place(relx=0.5, rely=0.37, anchor='center')
spielstandSpielerLabel = tk.Label(nummerFrame, text='Spieler X   :   Spieler O', font=custom_font15, bg=dark, fg=fontcol)
spielstandSpielerLabel.grid(row=0, column=0, columnspan=3)
spieler1Label = tk.Label(nummerFrame, text='0', font=custom_font, bg=dark, fg=fontcol)
spieler1Label.grid(row=1, column=0)
spieler2Label = tk.Label(nummerFrame, text='0', font=custom_font, bg=dark, fg=fontcol)
spieler2Label.grid(row=1, column=2)
resetSpielstand_btn = tk.Button(spielstandFrame, text='Reset Spielstand', font=custom_font15, command=resetSpielstand, bg=dark, border=3, fg=fontcol)
resetSpielstand_btn.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# Canvas
canvas = tk.Canvas(root, bg=between, width=size, height=size, highlightthickness=0)
canvas.place(relx=0.5, rely=0.5, anchor='center')
# Titel
titellabel = tk.Label(root, text='Tic Tac Toe', font=custom_font, bg=dark, fg=fontcol)
titellabel.place(relx=0.5, rely=0.1, anchor='center')
# countdown
countdown = tk.Label(root, text=f'{remainingTime} Sekunden', font=custom_font25, bg=dark, fg=fontcol)
countdown.place(relx=0.5, rely=0.9, anchor='center')

# Bindings
canvas.bind('<Button-1>', macheSpielzug)

################################################ Alle Sounds ##########################################################

# sound initializations
# Change the working directory to the directory the .py file is stored
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

pygame.mixer.init()

clickSound = pygame.mixer.Sound("sounds/click.mp3")
backgroundSound = pygame.mixer.Sound('sounds/background.mp3')
winSound = pygame.mixer.Sound('sounds/win.mp3')
unentschiedenSound = pygame.mixer.Sound('sounds/unentschieden.mp3')
intro = pygame.mixer.Sound('sounds/intro.mp3')

channel1 = pygame.mixer.Channel(0)  # Kanal für Sound 1
channel2 = pygame.mixer.Channel(1)  # Kanal für Sound 2
channel3 = pygame.mixer.Channel(2)  # Kanal für win und unentschieden sound
channel4 = pygame.mixer.Channel(3)  # Kanal für intro sound

################################################ Game Engine #########################################################

initializeGame()
updateAktuellerSpieler()
spielregelnWindow()
channel4.stop()
playSound('bg')
startCountdown()

# Mainloop
root.mainloop()