/**
 * Created by nitinpasumarthy on 5/5/16.
 *
 * Uses a state machine to suggest auto complete options
 * In Progress
 */

// Filter Textbox
let start = new State($scope.columns);
let filterExpr = new StateMachine(start); // key
filterExpr.next(new State(['>', '<', '=', '<=', '>='])); // operator
filterExpr.next(new State([], true)); // values
filterExpr.next(new State(['AND', 'OR'])); // combiner
filterExpr.next(start);
window.myState = filterExpr;
let filterTokens = [], states = [];

function suggest(request, response) {
    // console.log(filterExpr.current.values);
    response(filterExpr.current.values);
}

function moveToNextState(newItem) {
    filterTokens.push(newItem);
    this.value = filterTokens.join(" ") + " ";
    states.push(filterExpr.current); // TODO: handle when user starting modifying existing expression
    filterExpr.next(); // move to next state
    $scope.openSuggestions();
}

function getTokens(filterText) {
    // tokens are separated by a space
    return filterText.split(/\s+/);
}

function selected(event, ui) {
    moveToNextState.call(this, ui.item.value.trim());
    return false; // prevent default behavior of replacing the entire input field's value
}

$scope.openSuggestions = function () {
    $("#search").autocomplete("search"); // open suggestions
};
$("#search").bind('keypress', function (event) {
    if (event.keyCode === $.ui.keyCode.SPACE) {
        // Move to next state
        moveToNextState.call(this, getTokens(this.value.trim()).pop());
        event.preventDefault();
    }
}).autocomplete({
    source: suggest,
    select: selected, minLength: 0,
    focus: function () {
        return false;
    }
});

$("#search").autocomplete("disable"); // TODO: disabled until entire control is ready