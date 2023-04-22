from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask import Flask, render_template, request, url_for, redirect

# python -c 'import secrets; print(secrets.token_hex()) PARA criar uma chave aleatória

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database7teste.db'
app.config['TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '67022250fedb4dd9c6838019013fb1685dbc33f988b85c3e6a17f06fd82e5fcb' 
app.config['RECAPTCHA_PUBLIC_KEY'] = 'faf89031a5b03a72da5b759b27cbbd1d14916c1467c18fa309f5131fa19c6711'
app.config['RECAPTCHA_PRIVATE_KEY'] = 'vta757a2a2beb0e70b343fb802e4f35dd755b5c419d3533e7befc3546f103eb8' 
db = SQLAlchemy()
db.init_app(app)

class ClienteForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    idade = IntegerField('idade', validators=[NumberRange(min=1)])
    estado = StringField('estado', validators=[DataRequired()])
    cidade = StringField('cidade', validators=[DataRequired()])
    cidade_id = IntegerField('id da cidade')
    

class Cliente(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    nome = db.Column('nome', db.String(50), unique=True, nullable=False)
    idade = db.Column('idade', db.Integer, nullable=False)
    cidade_residente = db.relationship('Cidade', backref='cliente')

class Cidade(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    estado = db.Column('estado', db.String, nullable=False)
    cidade = db.Column('cidade', db.String, nullable=False)
    cliente_id =  db.Column(db.Integer, db.ForeignKey('cliente.id'))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    clientes = db.session.execute(db.select(Cliente).order_by(Cliente.nome)).scalars()
    cidades = db.session.execute(db.select(Cidade).order_by(Cidade.cidade)).scalars()
    return render_template('index.html', clientes=clientes, cidades=cidades)   

@app.route('/create', methods=['GET', 'POST'])
def create():
    form = ClienteForm()
    if form.validate_on_submit():
        user = Cliente(nome=form.nome.data, idade=form.idade.data)
        city = Cidade(estado=form.estado.data, cidade=form.cidade.data, cliente=user)
        db.session.add(user)
        db.session.add(city)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', form=form)

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    cliente = db.get_or_404(Cliente, id)
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = db.get_or_404(Cliente, id)
        cidade = db.get_or_404(Cidade, form.cidade_id.data)
        cidade.cidade = form.cidade.data
        cidade.estado = form.estado.data
        cliente.nome = form.nome.data
        cliente.idade = form.idade.data 
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update1.html', form=form, id=id, cliente=cliente)

@app.route('/delete/<int:id>')
def delete(id):
    cliente = db.get_or_404(Cliente, id)
    cidade = db.session.execute(db.select(Cidade).filter_by(cliente_id=id)).scalar_one()
    db.session.delete(cidade)
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run(debug=True)