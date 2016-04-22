/**
 * Created by nitinpasumarthy on 4/21/16.
 */

class State {
    /**
     * creates a new state
     * @param values possible values in this state
     * @param isFinish boolean which indicates if this is the finish state
     * @param next optional next state
     */
    constructor(values = [], isFinish = false, next = null) {
        this.values = values;
        this.isFinish = isFinish;
        this.next = next;
    }

    addNext(state) {
        this.next = state;
    }
}

class StateMachine {
    constructor(startState) {
        if (!startState)
            throw "To create a state machine, a start state is a must";
        this.current = startState;
    }

    next(state) {
        if (state) {
            this.current.addNext(state);
            this.on(state);
        }
        else
            this.current = this.current.next;

    }

    on(state) {
        if (state)
            this.current = state;
        else
            return this.current;
    }
}
