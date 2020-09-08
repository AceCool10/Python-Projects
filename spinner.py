from turtle import *

state = {'turn': 0}
#------------------------------------MAKE YOUR OWN SPINNER---------------------------------------------
def spinner():
    "Draw fidget spinner."                            #The gray text is just the original
    clear()
    angle = state['turn'] / 10
    right(angle)
    forward(100)
    dot(120, 'red')#red
    back(100)
    right(120)
    forward(100)
    dot(120, 'green')#green
    back(100)
    right(120)
    forward(100)
    dot(120, 'blue')#blue
    back(100)
    right(120)
    update()
#------------------------------------MAKE YOUR OWN SPINNER---------------------------------------------
def animate():
    "Animate fidget spinner."
    if state['turn'] > 0:
        state['turn'] -= 1

    spinner()
    ontimer(animate, 20)

def flick():
    "Flick fidget spinner."
    state['turn'] += 10

setup(420, 420, 370, 0)            #The screen stuff
hideturtle()
tracer(False)      #If "True" it would spin on its own and draw itself
width(25)          #Makes black thing thicker
onkey(flick, 'space')
listen()
animate()
done()