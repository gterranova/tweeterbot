/* global $:false, _:false */
'use strict';
angular.module('app', [
    'directives.parallax',
    'directives.tabs',
    'directives.countdown'
]);
angular.module('directives.parallax', [])
.directive('imgParallax', ['$window', '$parse', function($window, $parse){
    return {
        restrict: 'EAC',
        compile: function(element, attrs) {
            return function(scope, element, attrs) {
                element.css({ 'background-image': 'url(\''+attrs.value+'\')'});
                var w = $($window);
                var updateBackgroundPos = function () {
                    var yPos = -(w.scrollTop() * element.data('speed'));
                    //console.log("YPOS",yPos);
                    
                    // Put together our final background position
                    var coords = '50% ' + yPos + 'px';
                    //console.log("COORDS", coords);

                    // Move the background
                    element.css({ backgroundPosition: coords });
                };
                w.on('scroll', updateBackgroundPos);
                scope.$on('$destroy', function(){ stopWatch(); w.off('scroll', updateBackgroundPos); });
            }
        }
    };
}]);
angular.module('directives.tabs', [])
.controller('TabsController', ['$scope', '$window', function($scope, $window){
    $scope.tabs = [];
    $scope.currentTab = this.currentTab = 0;
    this.addTab = function(t) {
        $scope.tabs.push(t);
        
        if (t.tabSelected) {
            $scope.setCurrentTab($scope.tabs.length-1);
        } else {
            t.element.hide();
        };
        return $scope.tabs.length-1;
    };
    $scope.isFirstTab = function() {
        return $scope.currentTab === 0;
    };

    $scope.isLastTab = function() {
        return $scope.currentTab === ($scope.tabs.length - 1);
    };

    this.isCurrentTab = $scope.isCurrentTab = function(step) {
        return $scope.currentTab === step;
    };

    this.setCurrentTab = $scope.setCurrentTab = function(step) {
        if ($scope.tabs[step].tabEnabled) {
            if ($scope.tabs[step].tabUrl !== undefined && $window.location.pathname != $scope.tabs[step].tabUrl) {
                $window.location = $scope.tabs[step].tabUrl;
            } else {
                _.each($scope.tabs, function(tab, index) {
                    if (index !== step) {
                        tab.element.hide();
                    } else {
                        tab.element.show();
                    }
                });
                $scope.currentTab = step;
            }
        }
    };

    $scope.getCurrentTab = this.getCurrentTab = function() {
        return $scope.currentTab;
    };

    $scope.getNextLabel = function() {
        return ($scope.isLastTab()) ? 'Submit' : 'Next';
    };
    
    $scope.canHandleNext = function(step) {
        if (step===0) {
            return $scope.tabs[step].tabEnabled;
        } else {
            var can = $scope.tabs[step].tabEnabled && $scope.canHandleNext(step-1);
            if ($scope.tabs[step].tabPreviousRequired === true) {
                can = can && ($scope.getCurrentTab() >= (step-1) );
            }
            return can;
        }
    };
    
    $scope.handlePrevious = function() {
        var current = $scope.getCurrentTab();
        if (current > 0) {
            $scope.setCurrentTab(current - 1);
        }
    };

    $scope.handleNext = function(dismiss) {
        if($scope.isLastTab()) {
            dismiss();
        } else {
            $scope.setCurrentTab($scope.currentTab + 1);
        }
    };    
}])
.directive('tabs', [function(){
    return {
        restrict: 'EA',
        controller: 'TabsController',
        priority: 1000,
    };
}])
.directive('tabsMenu', [function(){
    return {
        restrict: 'EA',
        require: '^tabs',
        replace: true,
        controller: 'TabsController',
        template: '<ul>'+
                 '<li ng-repeat="t in tabs" ng-click="setCurrentTab($index)" ng-class="{active:isCurrentTab($index), disabled: !canHandleNext($index)}">'+
                 '<a ng-click="setCurrentTab($index)">{{t.tabHeading}}</a></li></ul>',
        priority: 1
    };
}])
.directive('tabsButtons', [function(){
    return {
        restrict: 'EA',
        require: '^tabs',
        scope: false,
        template: '<div class="tab-contents clearfix">'+
                 '<a class="btn btn-primary pull-left" ng-click="handlePrevious()" ng-show="!isFirstTab()"><i class="fa fa-chevron-left"></i>Back</a>'+
                 '<a class="btn btn-primary pull-right" ng-disabled="!canHandleNext(currentTab)"  ng-class="{disabled: !canHandleNext(currentTab)}" ng-click="handleNext(save)">{{getNextLabel()}}<i class="fa fa-chevron-right"></i></a>'+
                 '</div>',
        priority: 1,
    };
}])
.directive('tabsContents', ['$compile', function($compile){
    return {
        restrict: 'EA',
        require: '^tabs',
        scope: {
            'tabHeading': '@',  
            'tabSelected': '=', //
            'tabUrl': '@', //
            'tabEnabled': '=', //
            'tabHideTitle': '=',
            'tabPreviousRequired': '='//
        },
        priority: 1,
        transclude: true,
        template: '<div class="tab-contents clearfix">'+
                 '<div ng-if="!!!tabHideTitle"><h3>{{tabHeading}}</h3><hr/></div>'+
                 '<div></div>'+
                 '</div>',
        link: function(scope, element, attrs, tabsController, transclude) {
            scope.element = element;
            scope.tabSelected = scope.tabSelected == undefined ? false : scope.tabSelected;
            var newScope = scope.$parent.$new();
            newScope.$tabIndex = tabsController.addTab(scope);
            newScope.$currentTab = function() { return tabsController.getCurrentTab(); };
            newScope.$isCurrentTab = function() { return tabsController.getCurrentTab() === newScope.$tabIndex; };
            
            var isolatedScope = scope;
            transclude(newScope, function(clone, scope) {
                $('div:eq(1)', element).append(clone);
            });
            scope.$on('$destroy', function(){ newScope.$destroy(); });
        }            
    };
}]);
angular.module('directives.countdown', [])
.filter('timeRemaining', function() {
    return function(input) {
        var now = new Date().getTime() / 1000;
        var target_date = new Date(input);
        if (typeof target_date.getTime === 'function') {
            var target = target_date.getTime() / 1000;
            if (!isNaN(target) && target > now) {
                var sec = target-now,
                    days = Math.floor(sec / (3600 * 24)),
                    hours = Math.floor((sec-(days*24*3600))/3600),
                    minutes = Math.floor((sec-(days*24*3600)-(hours*3600))/60),
                    seconds = Math.floor(sec -(days*24*3600) - (hours * 3600) - (minutes * 60));
                return (days > 1? ""+ days + " days" : (days > 0? ""+ days + " day" : ("0"+hours).substr(-2)+":"+("0"+minutes).substr(-2)+":"+("0"+seconds).substr(-2)));
            }
        }
        return '00:00:00';
    };
})
.filter('timeElapsed', function() {
    return function(input) {
        var now = new Date().getTime() / 1000;
        var target_date = new Date(input);
        if (typeof target_date.getTime === 'function') {
            var target = target_date.getTime() / 1000;
            if (!isNaN(target) && target < now) {
                var sec = now-target,
                    days = Math.floor(sec / (3600 * 24)),
                    hours = Math.floor((sec-(days*24*3600))/3600),
                    minutes = Math.floor((sec-(days*24*3600)-(hours*3600))/60),
                    seconds = Math.floor(sec -(days*24*3600) - (hours * 3600) - (minutes * 60));
                return (days > 1? ""+ days + " days" : 
                       (days > 0? ""+ days + " day" : 
                       (hours > 1? ""+ hours + " hours" : 
                       (hours > 0? ""+ hours + " hour" : 
                       (minutes > 1? ""+ minutes + " minutes" : 
                       (minutes > 0? ""+ minutes + " minute" : 
                       (seconds > 1? ""+ seconds + " seconds" : 
                       "1 second")))))));
            }
        }
        return '0 seconds';
    };
})
.directive('timeRemaining', ['$filter', '$interval', function($filter, $interval){
    return {
        scope: {
            'date': '@'
        },
        restrict:'EA',
        template: '<span><span ng-if="!expired">{{timeRemaining}}</span><span ng-if="expired">Expired</span><span>',
        link: function(scope, element, attrs) {
            var timeFilter = $filter('timeRemaining');
            var target_date = new Date(scope.date);
            if (typeof target_date.getTime === 'function') {
                scope.target = target_date.getTime() / 1000;
            }
            function updateTime() {
                var now = new Date().getTime() / 1000;
                if (!isNaN(scope.target)) {
                    scope.expired = scope.target < now;
                    scope.timeRemaining = timeFilter(scope.date);
                    if (scope.target-now > 3600*24 || scope.expired) {
                        $interval.cancel(scope.interval);
                    }
                }
            }
            scope.interval = $interval(updateTime, 1000);
        }
    };
}])
.directive('timeElapsed', ['$filter', '$interval', function($filter, $interval){
    return {
        scope: {
            'date': '@'
        },
        restrict:'EA',
        template: '<span>{{timeElapsed}}</span>',
        link: function(scope, element, attrs) {
            var timeFilter = $filter('timeElapsed');
            var target_date = new Date(scope.date);
            if (typeof target_date.getTime === 'function') {
                scope.target = target_date.getTime() / 1000;
            }
            if (!isNaN(scope.target)) {
                scope.timeElapsed = timeFilter(scope.date);
            } else {
                scope.timeElapsed = 'some time';
            }
        }
    };
}]);
/*
  Bootstrap - File Input
  ======================

  This is meant to convert all file input tags into a set of elements that displays consistently in all browsers.

  Converts all
  <input type="file">
  into Bootstrap buttons
  <a class="btn">Browse</a>

*/
(function($) {

$.fn.bootstrapFileInput = function() {

  this.each(function(i,elem){

    var $elem = $(elem);

    // Maybe some fields don't need to be standardized.
    if (typeof $elem.attr('data-bfi-disabled') != 'undefined') {
      return;
    }

    // Set the word to be displayed on the button
    var buttonWord = 'Browse';

    if (typeof $elem.attr('title') != 'undefined') {
        if (!!$elem.attr('wrapper')) {
          var textWrapper = '' + $elem.attr('wrapper');
          buttonWord = $('<'+textWrapper+'></'+textWrapper+'>').html($elem.attr('title'));
        } else {
            buttonWord = $elem.attr('title');
        }
    }

    var className = '';
    var iconClassName = '';

    if (!!$elem.attr('class')) {
      className = ' ' + $elem.attr('class');
    }
        
    var buttonElement = $('<span></span>').html(buttonWord);

    if (!!$elem.attr('icon')) {
      iconClassName = ' ' + $elem.attr('icon');
      buttonElement.prepend($('<i class="'+iconClassName+'"></i>').append('&nbsp;'));
    }
    
    // Now we're going to wrap that input field with a Bootstrap button.
    // The input will actually still be there, it will just be float above and transparent (done with the CSS).
    $elem.wrap('<a class="file-input-wrapper ' + className + '"></a>').parent().prepend(buttonElement);
  })

  // After we have found all of the file inputs let's apply a listener for tracking the mouse movement.
  // This is important because the in order to give the illusion that this is a button in FF we actually need to move the button from the file input under the cursor. Ugh.
  .promise().done( function(){

    // As the cursor moves over our new Bootstrap button we need to adjust the position of the invisible file input Browse button to be under the cursor.
    // This gives us the pointer cursor that FF denies us
    $('.file-input-wrapper').mousemove(function(cursor) {

      var input, wrapper,
        wrapperX, wrapperY,
        inputWidth, inputHeight,
        cursorX, cursorY;

      // This wrapper element (the button surround this file input)
      wrapper = $(this);
      // The invisible file input element
      input = wrapper.find("input");
      // The left-most position of the wrapper
      wrapperX = wrapper.offset().left;
      // The top-most position of the wrapper
      wrapperY = wrapper.offset().top;
      // The with of the browsers input field
      inputWidth= input.width();
      // The height of the browsers input field
      inputHeight= input.height();
      //The position of the cursor in the wrapper
      cursorX = cursor.pageX;
      cursorY = cursor.pageY;

      //The positions we are to move the invisible file input
      // The 20 at the end is an arbitrary number of pixels that we can shift the input such that cursor is not pointing at the end of the Browse button but somewhere nearer the middle
      var moveInputX = cursorX - wrapperX - inputWidth + 20;
      // Slides the invisible input Browse button to be positioned middle under the cursor
      var moveInputY = cursorY- wrapperY - (inputHeight/2);

      // Apply the positioning styles to actually move the invisible file input
      input.css({
        left:moveInputX,
        top:moveInputY
      });
    });

    $('body').on('change', '.file-input-wrapper input[type=file]', function(){

      var fileName;
      fileName = $(this).val();

      // Remove any previous file names
      $(this).parent().next('.file-input-name').remove();
      if (!!$(this).prop('files') && $(this).prop('files').length > 1) {
        fileName = $(this)[0].files.length+' files';
      }
      else {
        fileName = fileName.substring(fileName.lastIndexOf('\\') + 1, fileName.length);
      }

      // Don't try to show the name if there is none
      if (!fileName) {
        return;
      }

      var selectedFileNamePlacement = $(this).data('filename-placement');
      if (selectedFileNamePlacement === 'inside') {
        // Print the fileName inside
        $(this).siblings('span').html(fileName);
        $(this).attr('title', fileName);
      } else {
        // Print the fileName aside (right after the the button)
        $(this).parent().after('<span class="file-input-name">'+fileName+'</span>');
      }
    });

  });

};

// Add the styles before the first stylesheet
// This ensures they can be easily overridden with developer styles
var cssHtml = '<style>'+
  '.file-input-wrapper { overflow: hidden; position: relative; cursor: pointer; z-index: 1; }'+
  '.file-input-wrapper input[type=file], .file-input-wrapper input[type=file]:focus, .file-input-wrapper input[type=file]:hover { position: absolute; top: 0; left: 0; cursor: pointer; opacity: 0; filter: alpha(opacity=0); z-index: 99; outline: 0; }'+
  '.file-input-name { margin-left: 8px; }'+
  '</style>';
$('link[rel=stylesheet]').eq(0).before(cssHtml);

})(jQuery);
