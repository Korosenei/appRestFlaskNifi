from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from marshmallow import Schema, fields, validate

db = SQLAlchemy()


class Client(db.Model):
    """Modèle Client"""
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    reservations = db.relationship('Reservation', backref='client', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Client {self.prenom} {self.nom}>'


class Chambre(db.Model):
    """Modèle Chambre"""
    __tablename__ = 'chambres'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    prix_par_nuit = db.Column(db.Numeric(10, 2), nullable=False)
    capacite = db.Column(db.Integer, nullable=False)
    disponible = db.Column(db.Boolean, default=True)

    # Relations
    reservations = db.relationship('Reservation', backref='chambre', lazy=True)

    def __repr__(self):
        return f'<Chambre {self.numero} - {self.type}>'


class Reservation(db.Model):
    """Modèle Réservation"""
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambres.id'), nullable=False)
    date_arrivee = db.Column(db.Date, nullable=False)
    date_depart = db.Column(db.Date, nullable=False)
    nombre_personnes = db.Column(db.Integer, nullable=False)
    prix_total = db.Column(db.Numeric(10, 2))
    statut = db.Column(db.String(20), default='confirmee')
    date_reservation = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reservation {self.id} - {self.statut}>'


class ReservationStaging(db.Model):
    """Modèle Staging pour données NiFi"""
    __tablename__ = 'reservations_staging'

    id = db.Column(db.Integer, primary_key=True)
    client_nom = db.Column(db.String(100))
    client_prenom = db.Column(db.String(100))
    client_email = db.Column(db.String(150))
    client_telephone = db.Column(db.String(20))
    chambre_numero = db.Column(db.String(10))
    chambre_type = db.Column(db.String(50))
    date_arrivee = db.Column(db.String(20))
    date_depart = db.Column(db.String(20))
    nombre_personnes = db.Column(db.String(10))
    prix_par_nuit = db.Column(db.String(20))
    statut = db.Column(db.String(20))
    date_import = db.Column(db.DateTime, default=datetime.utcnow)
    traite = db.Column(db.Boolean, default=False)


# Schémas Marshmallow pour sérialisation

class ClientSchema(Schema):
    """Schéma de sérialisation Client"""
    id = fields.Int(dump_only=True)
    nom = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    prenom = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    telephone = fields.Str(validate=validate.Length(max=20))
    date_creation = fields.DateTime(dump_only=True)
    reservations = fields.Nested('ReservationSchema', many=True, exclude=('client',))


class ChambreSchema(Schema):
    """Schéma de sérialisation Chambre"""
    id = fields.Int(dump_only=True)
    numero = fields.Str(required=True, validate=validate.Length(max=10))
    type = fields.Str(required=True, validate=validate.OneOf(['Simple', 'Double', 'Suite']))
    prix_par_nuit = fields.Decimal(required=True, as_string=True)
    capacite = fields.Int(required=True, validate=validate.Range(min=1))
    disponible = fields.Bool()


class ReservationSchema(Schema):
    """Schéma de sérialisation Réservation"""
    id = fields.Int(dump_only=True)
    client_id = fields.Int(required=True)
    chambre_id = fields.Int(required=True)
    date_arrivee = fields.Date(required=True)
    date_depart = fields.Date(required=True)
    nombre_personnes = fields.Int(required=True, validate=validate.Range(min=1))
    prix_total = fields.Decimal(as_string=True)
    statut = fields.Str(validate=validate.OneOf(['confirmee', 'annulee', 'terminee']))
    date_reservation = fields.DateTime(dump_only=True)

    # Relations imbriquées
    client = fields.Nested(ClientSchema, exclude=('reservations',))
    chambre = fields.Nested(ChambreSchema)


# Instanciation des schémas
client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)
chambre_schema = ChambreSchema()
chambres_schema = ChambreSchema(many=True)
reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)