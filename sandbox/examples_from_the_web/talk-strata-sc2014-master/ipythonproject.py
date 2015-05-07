from IPython.display import HTML, display

devs = [
    ('Fernando Perez', 'fperez.jpg'),
    ('Brian Granger', 'ellisonbg.jpg'),
    ('Min Ragan-Kelley', 'minrk.jpg'),
    ('Thomas Kluyver', 'takluyver.jpg'),
    ('Matthias Bussonnier', 'matthias.jpg'),
    ('Jonathan Frederic', 'jdfreder.jpg'),
    ('Paul Ivanov', 'ivanov.jpg'),
    ('Evan Patterson', 'epatters.jpg'),
    ('Damian Avila', 'damianavila.jpg'),
    ('Brad Froehle', 'brad.jpg'),
    ('Zach Sailer', 'zsailer.jpg'),
    ('Robert Kern', 'rkern.jpg'),
    ('Jorgen Stenarson', 'jorgen.jpg'),
    ('Jonathan March', 'jdmarch.jpg'),
    ('Kyle Kelley', 'rgbkrk.jpg')
]

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

s = "<table>"

for row in chunks(devs, 4):
    s += "<tr>"
    for person in row:
        s += "<td>"
        s += '<img src="ipythonteam/{image}" style="height: 150px; text-align: center; margin-left: auto; margin-right: auto;"/>'.format(image=person[1])
        s += '<h3 style="text-align: center;">{name}</h3>'.format(name=person[0])
        s += "</td>"
    s += "</tr>"
    
s += "</table>"

def core_devs():
    display(HTML(s))