import random
from flask import Flask, render_template, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_choice = db.Column(db.String(100), nullable=False)
    computer_choice = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'user_choice={self.user_choice}, computer_choice={self.computer_choice}, result={self.result})'


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    game_results = Users.query.order_by(Users.id.desc()).limit(10).all()
    return render_template('index.html', game_results=game_results)


def select_random_hand():
    hands = ["가위", "바위", "보"]
    return random.choice(hands)


@app.route('/submit', methods=['POST'])
def submit():
    choices = ['가위', '바위', '보']
    user_input = int(request.form['user_input'])
    user_choice = choices[user_input - 1]
    computer_choice = random.choice(choices)

    if user_choice == computer_choice:
        result = 'DRAW'
    elif (user_choice == '가위' and computer_choice == '보') or \
            (user_choice == '바위' and computer_choice == '가위') or \
            (user_choice == '보' and computer_choice == '바위'):
        result = 'WIN'
    else:
        result = 'LOSE'

    # 결과 저장
    game_result = Users(user_choice=user_choice, computer_choice=computer_choice, result=result)

    db.session.add(game_result)
    db.session.commit()

    print(f"User choice: {user_choice}, Computer choice: {computer_choice}, {result}")

    game_results = Users.query.order_by(Users.id.desc()).limit(10).all()
    game_results_dict = [{'user_choice': r.user_choice, 'computer_choice': r.computer_choice, 'result': r.result} for r
                         in game_results]

    return jsonify({
        'user_choice': user_choice,
        'computer_choice': computer_choice,
        'result': result,
        'game_results': game_results_dict
    })


if __name__ == '__main__':
    app.run(debug=True)
