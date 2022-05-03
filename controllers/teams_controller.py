from models import team_model
from utilities import utils
from database import db
import sqlalchemy


def show_all_teams():
    try:
        arr = team_model.Team.query.all()
        results = []
        for item in arr:
            item = vars(item)
            obj = {
                'full_team_name': item['full_team_name'],
                'name_slug': item['team_name_slug']
            }
            results.append(obj)
        return results
    except sqlalchemy.exc.OperationalError:
        return 'Operations error: possibily no table exists in DB'
    finally:
        db.session.close()


# takes either the team_name_slug or the team ID
def show_single_team(identifier):
    try:
        # check if it's ID
        if identifier.isdigit():
            try:
                team = vars(team_model.Team.query.filter_by(
                    id=identifier).first())
                return utils.serialize_row(team)
            except Exception as e:
                print('Error in team_controller.show_single_team ID', e)
        # or if it's name_slug
        else:
            try:
                team = vars(team_model.Team.query.filter_by(
                    team_name_slug=identifier).first())
                return utils.serialize_row(team)
            except Exception as e:
                print('Error in team_controller.show_single_team slug', e)
    finally:
        db.session.close()
