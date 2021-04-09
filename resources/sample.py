from flask.views import MethodView, request


'''This MethodView will be available at /sample/<key>'''

class SampleEndpoint(MethodView):
    '''
    This is another way for API structure using only flask
    Is is a bit simplier to implement but it comes with some disadvantages:
    1) Request parser is not available, so a low-level prototype of it should be writeen manually
    2) Maintainability
    3) Probably something else
    '''

    def get(self, key):
        '''Get object'''
        return {'method': request.method, 'key': key}

    def post(self, key, **payload):
        '''Create object'''
        return {'method': request.method, 'key': key, 'got': payload}

    '''
    Following three methods are very rare since all post method can comprehend all of their functionality
    But it is always useful to know them and their purpose
    '''


    def put(self, key, **payload):
        '''Create or replace object'''
        return {'method': request.method, 'key': key, 'got': payload}

    def patch(self, key, **payload):
        '''Update object'''
        return {'method': request.method, 'key': key, 'got': payload}
    
    def delete(self, key, **payload):
        '''Delete object'''
        return {'method': request.method, 'key': key, 'got': payload}