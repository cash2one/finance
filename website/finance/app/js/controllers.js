'use strict';

/* Controllers */

function financeCtrl($scope, $rootScope, $location) {
    $rootScope.$on('$routeChangeSuccess', function(event, routeData) {
        if (routeData.$route) {
            $scope.secure = routeData.$route.secure;
        }
    });
}

function FinanceCtrlLogin(scope, http, location, tokenHandler, api_url) {
    scope.response = "";
    scope.login = function() {
        scope.response = "";
        http.post(api_url.replace('\\', '') + '/login', scope.user).
            success(function(data){
                // set token
                tokenHandler.set(data.auth_token);
                // redirect to accounts page
                location.path("/accounts");
            }).
            error(function(data){
                scope.response = data.message;
            });
    }
}
FinanceCtrlLogin.$inject = ['$scope', '$http', '$location', 'tokenHandler', 'api_url'];


function FinanceCtrlAccounts(scope, AccountService) {
    scope.accounts = AccountService.query();
}
FinanceCtrlAccounts.$inject = ['$scope', 'Account'];
