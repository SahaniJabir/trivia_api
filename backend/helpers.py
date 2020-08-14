from flask import request, abort

QUESTIONS_PER_PAGE = 10


def paginated_questions_all(request, selection):
    page = request.args.get('page', 1, type=int)

    if page < 1:
        return abort(422)

    begin = (page - 1) * QUESTIONS_PER_PAGE
    end = begin + QUESTIONS_PER_PAGE
    questions = [question.format()for question in selection]

    return questions[begin:end]
