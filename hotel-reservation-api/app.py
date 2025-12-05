from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import (
    db, Client, Chambre, Reservation, ReservationStaging,
    client_schema, clients_schema, chambre_schema, chambres_schema,
    reservation_schema, reservations_schema
)
from datetime import datetime
from marshmallow import ValidationError


def create_app(config_name='default'):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)
    CORS(app)

    # Contexte de l'application
    with app.app_context():
        db.create_all()

    # ==================== ROUTES CLIENTS ====================

    @app.route('/api/clients', methods=['GET'])
    def get_clients():
        """Récupérer tous les clients avec pagination"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        clients = Client.query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'data': clients_schema.dump(clients.items),
            'pagination': {
                'page': clients.page,
                'per_page': clients.per_page,
                'total': clients.total,
                'pages': clients.pages
            }
        }), 200

    @app.route('/api/clients/<int:client_id>', methods=['GET'])
    def get_client(client_id):
        """Récupérer un client spécifique"""
        client = Client.query.get_or_404(client_id)
        return jsonify({
            'success': True,
            'data': client_schema.dump(client)
        }), 200

    @app.route('/api/clients', methods=['POST'])
    def create_client():
        """Créer un nouveau client"""
        try:
            data = client_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'errors': err.messages
            }), 400

        # Vérifier si l'email existe déjà
        if Client.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Un client avec cet email existe déjà'
            }), 409

        client = Client(**data)
        db.session.add(client)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Client créé avec succès',
            'data': client_schema.dump(client)
        }), 201

    @app.route('/api/clients/<int:client_id>', methods=['PUT'])
    def update_client(client_id):
        """Mettre à jour un client"""
        client = Client.query.get_or_404(client_id)

        try:
            data = client_schema.load(request.json, partial=True)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'errors': err.messages
            }), 400

        # Vérifier l'unicité de l'email si modifié
        if 'email' in data and data['email'] != client.email:
            if Client.query.filter_by(email=data['email']).first():
                return jsonify({
                    'success': False,
                    'message': 'Cet email est déjà utilisé'
                }), 409

        for key, value in data.items():
            setattr(client, key, value)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Client mis à jour',
            'data': client_schema.dump(client)
        }), 200

    @app.route('/api/clients/<int:client_id>', methods=['DELETE'])
    def delete_client(client_id):
        """Supprimer un client"""
        client = Client.query.get_or_404(client_id)
        db.session.delete(client)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Client supprimé'
        }), 200

    # ==================== ROUTES CHAMBRES ====================

    @app.route('/api/chambres', methods=['GET'])
    def get_chambres():
        """Récupérer toutes les chambres"""
        type_chambre = request.args.get('type')
        disponible = request.args.get('disponible')

        query = Chambre.query

        if type_chambre:
            query = query.filter_by(type=type_chambre)

        if disponible is not None:
            disponible_bool = disponible.lower() == 'true'
            query = query.filter_by(disponible=disponible_bool)

        chambres = query.all()

        return jsonify({
            'success': True,
            'data': chambres_schema.dump(chambres)
        }), 200

    @app.route('/api/chambres/<int:chambre_id>', methods=['GET'])
    def get_chambre(chambre_id):
        """Récupérer une chambre spécifique"""
        chambre = Chambre.query.get_or_404(chambre_id)
        return jsonify({
            'success': True,
            'data': chambre_schema.dump(chambre)
        }), 200

    @app.route('/api/chambres', methods=['POST'])
    def create_chambre():
        """Créer une nouvelle chambre"""
        try:
            data = chambre_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'errors': err.messages
            }), 400

        # Vérifier si le numéro existe déjà
        if Chambre.query.filter_by(numero=data['numero']).first():
            return jsonify({
                'success': False,
                'message': 'Une chambre avec ce numéro existe déjà'
            }), 409

        chambre = Chambre(**data)
        db.session.add(chambre)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chambre créée avec succès',
            'data': chambre_schema.dump(chambre)
        }), 201

    @app.route('/api/chambres/<int:chambre_id>', methods=['PUT'])
    def update_chambre(chambre_id):
        """Mettre à jour une chambre"""
        chambre = Chambre.query.get_or_404(chambre_id)

        try:
            data = chambre_schema.load(request.json, partial=True)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'errors': err.messages
            }), 400

        for key, value in data.items():
            setattr(chambre, key, value)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chambre mise à jour',
            'data': chambre_schema.dump(chambre)
        }), 200

    @app.route('/api/chambres/<int:chambre_id>', methods=['DELETE'])
    def delete_chambre(chambre_id):
        """Supprimer une chambre"""
        chambre = Chambre.query.get_or_404(chambre_id)
        db.session.delete(chambre)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chambre supprimée'
        }), 200

    # ==================== ROUTES RÉSERVATIONS ====================

    @app.route('/api/reservations', methods=['GET'])
    def get_reservations():
        """Récupérer toutes les réservations"""
        statut = request.args.get('statut')
        client_id = request.args.get('client_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = Reservation.query

        if statut:
            query = query.filter_by(statut=statut)

        if client_id:
            query = query.filter_by(client_id=client_id)

        reservations = query.order_by(Reservation.date_reservation.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'success': True,
            'data': reservations_schema.dump(reservations.items),
            'pagination': {
                'page': reservations.page,
                'per_page': reservations.per_page,
                'total': reservations.total,
                'pages': reservations.pages
            }
        }), 200

    @app.route('/api/reservations/<int:reservation_id>', methods=['GET'])
    def get_reservation(reservation_id):
        """Récupérer une réservation spécifique"""
        reservation = Reservation.query.get_or_404(reservation_id)
        return jsonify({
            'success': True,
            'data': reservation_schema.dump(reservation)
        }), 200

    @app.route('/api/reservations', methods=['POST'])
    def create_reservation():
        """Créer une nouvelle réservation"""
        try:
            data = reservation_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'errors': err.messages
            }), 400

        # Vérifier que le client existe
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({
                'success': False,
                'message': 'Client introuvable'
            }), 404

        # Vérifier que la chambre existe et est disponible
        chambre = Chambre.query.get(data['chambre_id'])
        if not chambre:
            return jsonify({
                'success': False,
                'message': 'Chambre introuvable'
            }), 404

        if not chambre.disponible:
            return jsonify({
                'success': False,
                'message': 'Chambre non disponible'
            }), 400

        # Calculer le prix total
        if 'prix_total' not in data or data['prix_total'] is None:
            nb_nuits = (data['date_depart'] - data['date_arrivee']).days
            data['prix_total'] = float(chambre.prix_par_nuit) * nb_nuits

        reservation = Reservation(**data)
        db.session.add(reservation)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Réservation créée avec succès',
            'data': reservation_schema.dump(reservation)
        }), 201

    @app.route('/api/reservations/<int:reservation_id>', methods=['PUT'])
    def update_reservation(reservation_id):
        """Mettre à jour une réservation"""
        reservation = Reservation.query.get_or_404(reservation_id)

        try:
            data = reservation_schema.load(request.json, partial=True)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'errors': err.messages
            }), 400

        for key, value in data.items():
            setattr(reservation, key, value)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Réservation mise à jour',
            'data': reservation_schema.dump(reservation)
        }), 200

    @app.route('/api/reservations/<int:reservation_id>/cancel', methods=['PUT'])
    def cancel_reservation(reservation_id):
        """Annuler une réservation"""
        reservation = Reservation.query.get_or_404(reservation_id)
        reservation.statut = 'annulee'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Réservation annulée',
            'data': reservation_schema.dump(reservation)
        }), 200

    @app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
    def delete_reservation(reservation_id):
        """Supprimer une réservation"""
        reservation = Reservation.query.get_or_404(reservation_id)
        db.session.delete(reservation)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Réservation supprimée'
        }), 200

    # ==================== ROUTES STATISTIQUES ====================

    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Obtenir des statistiques générales"""
        total_clients = Client.query.count()
        total_chambres = Chambre.query.count()
        chambres_disponibles = Chambre.query.filter_by(disponible=True).count()
        total_reservations = Reservation.query.count()
        reservations_confirmees = Reservation.query.filter_by(statut='confirmee').count()
        reservations_annulees = Reservation.query.filter_by(statut='annulee').count()

        return jsonify({
            'success': True,
            'data': {
                'clients': total_clients,
                'chambres': {
                    'total': total_chambres,
                    'disponibles': chambres_disponibles,
                    'occupees': total_chambres - chambres_disponibles
                },
                'reservations': {
                    'total': total_reservations,
                    'confirmees': reservations_confirmees,
                    'annulees': reservations_annulees
                }
            }
        }), 200

    # ==================== ROUTE RACINE ====================

    @app.route('/')
    def index():
        """Page d'accueil de l'API"""
        return jsonify({
            'message': 'Bienvenue sur l\'API de réservation d\'hôtel',
            'version': '1.0',
            'endpoints': {
                'clients': '/api/clients',
                'chambres': '/api/chambres',
                'reservations': '/api/reservations',
                'stats': '/api/stats'
            }
        }), 200

    # ==================== GESTION D'ERREURS ====================

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Ressource introuvable'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)