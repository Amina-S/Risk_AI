import random


def blitz(attack, defense):
    '''
    Does blitz roll until the defending side is destroyed or the attacker
        only has 1 troop left.
    Returns a tuple representing the remaining troops for attacker and defender,
        respectively (if the second entry is 0, attack was successful; if
        the first entry is 1, attack was unsuccessful).

    Preconditions: [attack] and [defense] are both positive integers.
    [attack] is bigger than 1.
    '''
    if attack <= 1:
        raise ValueError("Attacker has to have >1 troops!")
    if defense <= 0:
        raise ValueError("Defender has to have >0 troops!")
    a = attack
    d = defense

    while a > 1 and d > 0:
        if a >= 4 and d >= 2:
            # Both attacker and defender have enough troops for a 3-2 dice roll.
            curr_roll = roll(3, 2)
            print(curr_roll)
            a, d = write_res(a, d, curr_roll)
        elif d >= 2:
            # Attacker isn't strong enough for a 3-2 dice roll.
            curr_roll = roll(a-1, 2)
            print(curr_roll)
            a, d = write_res(a, d, curr_roll)
        elif a >= 4:
            # Defender isn't strong enough for a 3-2 dice roll.
            curr_roll = roll(3, 1)
            print(curr_roll)
            a, d = write_res(a, d, curr_roll)
        else:
            # Both aren't strong enough for a 3-2 dice roll.
            curr_roll = roll(a-1, 1)
            print(curr_roll)
            a, d = write_res(a, d, curr_roll)

    return (a, d)


def roll(dice_attack, dice_defend):
    '''
    A single roll that returns 2 if defender loses two troops (only
        possible if attacker rolls at least 2 dice); 1 if defender loses one
        troop (only possible if defender rolls 1 die); 0 if both sides lose one
        troop each; -1 if attacker loses one troop (only possible if defender
        rolls 1 die); -2 if attacker loses two troops (only possible if
        defender rolls at least 2 dice AND attacker rolls at least 2 dice).

    Preconditions: [dice_attack] and [dice_defend] are integers.
        1 <= [dice_attack] <= 3; 1 <= [dice_defend] <=2.
    '''
    assert type(dice_attack) == int and type(dice_defend) == int
    assert 1 <= dice_attack and dice_attack <= 3, "Number of attacking dice has to be between 1 and 3, inclusively!"
    assert 1 <= dice_defend and dice_defend <= 2, "Number of defending dice has to be between 1 and 2, inclusively!"

    attack_rolls = []
    defend_rolls = []

    for _ in range(dice_attack):
        attack_rolls.append(random.randint(1, 6))

    for _ in range(dice_defend):
        defend_rolls.append(random.randint(1, 6))

    attack_rolls.sort(reverse=True)
    defend_rolls.sort(reverse=True)

    print(attack_rolls)
    print(defend_rolls)

    if dice_attack == 1 or dice_defend == 1:
        if attack_rolls[0] > defend_rolls[0]:
            return 1
        else:
            return -1
    else:
        if attack_rolls[0] > defend_rolls[0] and attack_rolls[1] > defend_rolls[1]:
            return 2
        elif (attack_rolls[0] > defend_rolls[0]) or (attack_rolls[1] > defend_rolls[1]):
            return 0
        else:
            return -2


def write_res(attack, defense, roll_res):
    ''' Changes the numbers of [attack] and [defense] based on [roll_res]
            (obtained using roll()). For more details, see description of roll().
        Returns a new tuple for attacker and defender, respectively.

        Preconditions: [attack] and [defense] are positive integers that are big 
            enough to sustain losses described by [roll_res]. 
            -2 <= [roll_res] <= 2.'''
    assert attack > 1, "Not enough attacking troops!"
    if roll_res == 2:
        assert defense >= 2, "Not enough defending troops!"
        return (attack, defense-2)
    elif roll_res == 1:
        assert defense >= 1, "Not enough defending troops!"
        return (attack, defense-1)
    elif roll_res == 0:
        assert attack >= 2, "Not enough attacking troops!"
        assert defense >= 1, "Not enough defending troops!"
        return (attack-1, defense-1)
    elif roll_res == -1:
        assert attack >= 2, "Not enough attacking troops!"
        return (attack-1, defense)
    elif roll_res == -2:
        assert attack >= 3, "Not enough attacking troops!"
        return (attack-2, defense)
    else:
        raise ValueError("Wrong value for [roll_res]!")
