from flask import Flask, request, redirect, g, render_template, session, url_for, flash
from flask_ask import Ask, statement, question, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import pickle

app = Flask(__name__)
ask = Ask(app, '/')
app.secret_key = 'DFBK2L9X6nD,sqfFkCaJtN'
counter = -1

def save_speech(speeches):
    """ Writes databases as pickled file. Expects list """
    try:
        with open('speeches.pickle', 'wb') as handle:
            pickle.dump(speeches, handle, protocol=pickle.HIGHEST_PROTOCOL)
    except:
        pass
    return

def load_speech():
    """ Loads speech list, returns """

    try:
        with open('speeches.pickle', 'rb') as handle:
            data = pickle.load(handle)
    except:
        pass
        #logging.info("Loading friendList failed.")
    return data

speeches =  [['Eingabe1', 'Name1', 'Das behaupten jedenfalls:'],['Eingabe2', 'Name2', 'Das ist die unmaßgebliche Meinung von'],['Eingabe3', 'Name3', 'Wer mir das in den Mund gelegt hat?'],['Eingabe4', 'Name4', 'Sowas kommt auch nur von'],['Eingabe5', 'Name5', 'Habe ich das wirklich gesagt, Gruppe'],['Eingabe6', 'Name6', 'Das hab nicht ich mir ausgedacht, sondern'],]
save_speech(speeches)


class speech_eingabe(Form):
    speech_inhalt = TextField('Text:', validators=[validators.required(message='Utterance darf nicht leer sein'), validators.Length(min=10, max=1000, message='Utterance muss zwischen 10 und 1000 Zeichen enthalten.')])
    name = TextField('Namen der Mitglieder:', validators=[validators.required(message='Name darf nicht leer sein')])

@ask.launch
def launch():
    speech_text = 'Hallo. Ich bin die Neue am Empfang der Texterschmiede. Sage Wer bist du oder Stop'
    reprompt_text = 'Sage Wer bist du oder Stop'
    return question(speech_text).reprompt(reprompt_text)


@ask.intent('introduction')
def introduction():
    global counter
    counter += 1
    if counter > 5:
        counter = 0
    speech_loaded = load_speech()
    speech_text = speech_loaded[counter][0] + ' ' + speech_loaded[counter][2] + ' ' + speech_loaded[counter][1]
    reprompt_text = 'Sage Wer bist du oder Stop'
    return question(speech_text).reprompt(reprompt_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'Dieser Skill kann nicht viel. Sage nur wer bist du!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200

@app.route('/')
def home():
    return 'Hello 2'

@app.route('/dashboard')
def dashboard():
    global counter
    speech_list = load_speech()
    return render_template('dashboard.html',
                            speeches = speech_list,
                            counter = counter,
                            )

@app.route('/gruppe/<nummerAufr>', methods=['GET', 'POST'])
def gruppeMain(nummerAufr):

    error = False

    if request.method == 'POST':
        speech_inhalt=request.form['speech_inhalt']
        name=request.form['name']

    form = speech_eingabe(request.form)
    session.pop('_flashes', None)


    if not form.validate():
        error = True
        for field, errors in form.errors.items():
            for error in errors:
                flash("Feld \'%s\' %s" % (
                    getattr(form, field).label.text,
                    error))

    if int(nummerAufr) > 6:
        error = True
        flash('Link falsch. Bitte Oliver anhauen.')

    if not error and form.speech_inhalt.data:
        speeches = load_speech()
        connecting = speeches[int(nummerAufr)-1][2]
        speeches[int(nummerAufr)-1] = [speech_inhalt, name, connecting]
        save_speech(speeches)
        flash('Daten gespeichert')

    return render_template('gruppen.html',
                            grNummer = nummerAufr,
                            form=form,
                            )

if __name__ == '__main__':
    app.run()

