% to check adjacent
adjacent((X1, Y1), (X2, Y2)) :-
    (X2 is X1 + 1, Y2 is Y1);
    (X2 is X1 - 1, Y2 is Y1);
    (X2 is X1, Y2 is Y1 + 1);
    (X2 is X1, Y2 is Y1 - 1).

% breeze, glitter, and fall
breeze((X, Y)) :- adjacent((X, Y), Pit), pit(Pit).
glitter((X, Y)) :- gold((X, Y)).
fall((X, Y)) :- pit((X, Y)).

% Breeze checker by using adjacent on all pits
findBreeze((X, Y)) :- adjacent((X, Y), Pit), pit(Pit).

% Compares all breezes found so far
% Compares all breezes found so far
findPit((X, Y)) :-
    % dont check if it is a pit if it was a previously explored spot
    \+ explored((X, Y)),

    % Find all adjacent breeze spots
    findall((AdjX, AdjY), (adjacent((X, Y), (AdjX, AdjY)), breezeSpot((AdjX, AdjY))), BreezeSpots),

    % Check if there are enough breeze spots
    length(BreezeSpots, Count),
    Count >= 3.

safeConfirm((X, Y)) :-
    findall((AdjX, AdjY), (adjacent((X, Y), (AdjX, AdjY)), explored((AdjX, AdjY))), Explored),

    % Check if there are enough breeze spots
    length(Explored, Count),
    Count >= 4.
