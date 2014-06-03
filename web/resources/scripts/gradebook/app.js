// Generated by CoffeeScript 1.7.1
(function() {
  var gradebook, _;

  _ = window._;

  gradebook = angular.module('gradebook-app', ['ngCookies', 'gradebook']);

  gradebook.run([
    '$http', '$cookies', function($http, $cookies) {
      $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
      return $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
    }
  ]);

  gradebook.controller('ClassSelect', function($scope, $http, $rootScope) {
    $scope.classes = [];
    $http.get('/api/classes/taughtByMe/').success(function(result) {
      return angular.forEach(result, function(item) {
        return $scope.classes.push(item);
      });
    });
    return $scope.loadGradeBook = function(id) {
      return $rootScope.gradebook_id = id;
    };
  });

  gradebook.controller('gradebook-view', function($scope, $rootScope, $http) {
    var class_id, refreshGradingScale, refreshWeights;
    class_id = refreshWeights = true;
    refreshGradingScale = true;
    $rootScope.$watch('gradebook_id', function() {
      if (!$rootScope.gradebook_id) {
        return;
      }
      $http.get('/api/classes/' + $rootScope.gradebook_id + '/gradebook/').success(function(result) {
        $scope.breadcrumb = result.breadcrumb;
        $scope.events = result.events;
        $scope.gradebook = result.gradebook;
        $scope.students = result.students;
        class_id = $rootScope.gradebook_id;
        return $rootScope.$broadcast('recalculateAverages');
      });
      refreshWeights = true;
      refreshGradingScale = true;
      $scope.displayWeightControl = false;
      return $scope.showGradingScale = false;
    });
    $scope.toggleWeightControl = function() {
      if (refreshWeights) {
        $http.get('/api/classes/' + class_id + '/weights/').success(function(result) {
          $scope.weights = result;
          return refreshWeights = false;
        });
      }
      return $scope.displayWeightControl = !$scope.displayWeightControl;
    };
    return $scope.toggleGradingScale = function() {
      if (refreshGradingScale) {
        $http.get('/api/classes/' + class_id + '/gradingScale/').success(function(result) {
          $scope.gradingScale = result;
          return $scope.updateUppers();
        });
        refreshGradingScale = false;
      }
      return $scope.showGradingScale = !$scope.showGradingScale;
    };
  });

  gradebook.directive('wc', [
    '$http', '$rootScope', function($http, $rootScope) {
      return {
        restrict: 'AE',
        templateUrl: '../templates/gradebook/weights.html',
        link: function(scope, elem, attrs) {
          scope.addCategory = function() {
            if (scope.newCategory && scope.newPercentage) {
              scope.weights.categories.push({
                category: scope.newCategory,
                percentage: scope.newPercentage
              });
              scope.newCategory = null;
              scope.newPercentage = null;
            } else {

            }
            return scope.canSubmitWidget = scope.canSubmit();
          };
          scope.canSubmit = function() {
            var percentages, sum;
            if (!scope.weights) {
              return true;
            }
            percentages = _.pluck(scope.weights.categories, 'percentage');
            sum = _.reduce(percentages, function(memo, num) {
              return memo + parseInt(num);
            }, 0);
            if (sum === 100) {
              return true;
            } else {
              return false;
            }
          };
          scope.removeCategory = function(index) {
            scope.weights.categories.splice(index, 1);
            return scope.canSubmitWidget = scope.canSubmit();
          };
          return scope.updateWeights = function() {
            if (!scope.canSubmitWidget) {
              return;
            }
            return $http.post('/gradebook/weights/set/', {
              'classId': $rootScope.gradebook_id,
              'weights': scope.weights
            }).success(function(result) {
              scope.toggleWeightControl();
              $rootScope.$broadcast('recalculateWeights');
              $rootScope.$broadcast('recalculateGrades');
              return $rootScope.$broadcast('recalculateAverages');
            });
          };
        }
      };
    }
  ]);

  gradebook.directive('gsc', [
    '$http', '$rootScope', function($http, $rootScope) {
      return {
        restrict: 'AE',
        templateUrl: '../templates/gradebook/gradingScale.html',
        link: function(scope, elem, attrs) {
          scope.updateUppers = function() {
            return angular.forEach(scope.gradingScale.categories, function(category, key) {
              var cont, prev;
              cont = true;
              if (key === 0) {
                category.upper = 100;
                cont = false;
              }
              if (cont) {
                prev = scope.gradingScale.categories[key - 1];
                return category.upper = prev.lower;
              }
            });
          };
          scope.updateLowers = function() {
            return angular.forEach(scope.gradingScale.categories, function(category, key) {
              var cont, next;
              cont = true;
              if (key === scope.gradingScale.categories.length - 1) {
                category.lower = 0;
                cont = false;
              }
              if (cont) {
                next = scope.gradingScale.categories[key + 1];
                return category.lower = next.upper;
              }
            });
          };
          scope.deleteGradingScaleCategory = function(lower) {
            var cat;
            cat = _.findWhere(scope.gradingScale.categories, {
              lower: lower
            });
            scope.gradingScale.categories.splice(_.indexOf(scope.gradingScale.categories, cat), 1);
            return scope.updateUppers();
          };
          scope.addGradingScaleCategory = function(upper) {
            var additional, cat, index, next;
            cat = _.findWhere(scope.gradingScale.categories, {
              upper: upper
            });
            index = _.indexOf(scope.gradingScale.categories, cat);
            next = scope.gradingScale.categories[index - 1];
            additional = {
              upper: (next.upper + cat.upper) / 2,
              value: cat.value
            };
            scope.gradingScale.categories.splice(index, 0, additional);
            return scope.updateLowers();
          };
          return scope.applyGradingScale = function() {
            return $http.post('/gradebook/gradingScale/setScale/', {
              gradingScale: scope.gradingScale,
              classId: $rootScope.gradebook_id
            }).success(function(result) {
              $rootScope.$broadcast('recalculateGrades');
              return scope.toggleGradingScale();
            });
          };
        }
      };
    }
  ]);

}).call(this);
