from IPython.display import HTML, display

devs = [
    # Fields: name, picture, full time? (true/false)

    ('Fernando Perez', 'fperez.jpg', 1),
    ('Brian Granger', 'ellisonbg.jpg', 1),
    ('Min Ragan-Kelley', 'minrk.jpg', 1),
    ('Thomas Kluyver', 'takluyver.jpg', 1),
    ('Matthias Bussonnier', 'matthias.jpg', 0),
    ('Jonathan Frederic', 'jdfreder.jpg', 1),
    ('Paul Ivanov', 'ivanov.jpg', 1),
    ('Damian Avila', 'damianavila.jpg', 0),
    ('Kyle Kelley', 'rgbkrk.jpg', 0),
    ('Zach Sailer', 'zsailer.jpg', 0),
    ('Jorgen Stenarson', 'jorgen.jpg', 0),
    ('Jonathan March', 'jdmarch.jpg', 0),
    ('Brad Froehle', 'brad.jpg', 0),
    ('Evan Patterson', 'epatters.jpg', 0),
    ('Robert Kern', 'rkern.jpg', 0),
]


def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def devs_table(ncols=5, pic_height='130px', table_width='95%'):
    s = '<center>'
    s += '<h2>IPython Core Developers</h2>'
    s += '<table width="{}%">'.format(table_width)

    for row in chunks(devs, ncols):
        s += "<tr>"
        for name, image, full_time in row:
            s += "<td>"
            s += ('<img src="ipythonteam/{image}" style="height: {height}; '
                  'text-align: center; margin-left: auto; margin-right: auto'
                  ';"/>'.format(image=image, height=pic_height))
            # Larger heading style (bolded in CSS) to denote full-time devs
            h = 5 if full_time else 6
            s += '<h{h}><style="text-align:center;">{name}</h{h}>'.format(name=name,  h=h)
            #s += person[0]
            s += "</td>"
        s += "</tr>"

    s += "</table>"
    s += "</center>"
    return HTML(s)


def core_devs():
    display(devs_table())
