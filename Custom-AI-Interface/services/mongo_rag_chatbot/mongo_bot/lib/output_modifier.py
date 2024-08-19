"""Parse LLM output response."""
import re




def update_regex_pattern(query: str) -> str:
    """Update regex pattern in string.


    Args:
        query (str): Query as string


    Returns:
        str: Updated query
    """
    if "$regex" not in query:
        return query
    regex_patterns_part = query.split("$regex")
    new_list = []
    for item in regex_patterns_part:
        try:
            start = item.index("/")
            end = item.rindex("/")
            if len(item) > end + 1 and item[end + 1] == "i":
                end += 1
            new_item = f'"{item[start+1:end]}"'
            if new_item not in item:
                # pylint: disable=E203
                new_list.append(
                    item[0:start] + new_item + item[end + 1 :]  # noqa
                )  # noqa
            else:
                new_list.append(item)
        except ValueError:
            new_list.append(item)
    return "$regex".join(new_list)




def update_query(query: str) -> str:
    """Add correction to query.


    Args:
        query (str): MongoDB query


    Returns:
        str: Modified query
    """
    query = query.replace("None", "null")  # as None is not a valid json obj
    operators = [
        "$eq",
        "$ne",
        "$in",
        "$and",
        "$not",
        "$nor",
        "$or",
        "$regex",
        "$exists",
        "$where",
        "$expr",
        "$where",
        "$push",
        "$match",
        "$group",
        "$max",
        "$sort",
        "$min",
        "$limit",
        "$sum",
        "$avg",
    ]
    for operator in operators:
        if operator in query and f'"{operator}"' not in query:
            query = query.replace(operator, f'"{operator}"')


    i = 0
    new_query = ""


    while i < len(query) - 3:
        # pylint: disable=E203
        if query[i : i + 3] == "$gt":  # noqa
            if (
                query[i : i + 4] == "$gte"  # noqa
                and query[i - 1 : i + 5] != '"$gte"'  # noqa
            ):  # noqa
                new_query += '"$gte"'
                i += 4
            elif (
                query[i - 1 : i + 4] != '"$gt"'  # noqa
                and query[i - 1 : i + 5] != '"$gte"'  # noqa
            ):  # noqa
                new_query += '"$gt"'
                i += 3
            else:
                new_query += query[i]
                i += 1
        # pylint: disable=E203
        elif query[i : i + 3] == "$lt":  # noqa
            if (
                query[i : i + 4] == "$lte"  # noqa
                and query[i - 1 : i + 5] != '"$lte"'  # noqa
            ):  # noqa
                new_query += '"$lte"'
                i += 4
            elif (
                query[i - 1 : i + 4] != '"$lt"'  # noqa
                and query[i - 1 : i + 5] != '"$lte"'  # noqa
            ):  # noqa
                new_query += '"$lt"'
                i += 3
            else:
                new_query += query[i]
                i += 1


        else:
            new_query += query[i]
            i += 1


    new_query += query[i:]


    query = new_query


    return update_regex_pattern(query)




def get_pymongo_method(output: str) -> str:
    """Get pymongo method.


    Args:
        output (str): LLM response


    Returns:
        str: pymongo method
    """
    command = get_pymongo_command(output)


    first_brace_idx = command.index("(")
    # Find the method part
    method = command[:first_brace_idx].split(".")[-1]
    return method




def get_pymongo_command(output: str) -> str:
    """Get pymongo command.


    Args:
        output (str): LLM response


    Returns:
        str: pymongo command
    """
    pattern = r"`+(.*?)`+"
    matches = re.findall(pattern, output, re.DOTALL)
    if len(matches) > 0:
        matches[0] = matches[0].replace(
            "\n", ""
        )  # to remove all unnecessary newline characters
    else:
        matches = output


    # Join the lines in the input to create a single string
    return "".join(matches)




def get_find_query(input_text: str) -> str:
    """Get Find query from string.


    Args:
        input_text (str): Query as string


    Returns:
        str: Find query
    """
    first_brace_idx = input_text.index("{")
    last_brace_idx = input_text.rindex("}")
    query = input_text[first_brace_idx : last_brace_idx + 1]  # noqa
    query = query.replace("  ", "")  # To replace unwanted extra spaces
    return update_query(query)




def get_aggregate_query(input_text: str) -> str:
    """Get Aggregate query from string.


    Args:
        input_text (str): Query as string


    Returns:
        str: Aggregate query
    """
    first_brace_idx = input_text.index("[")
    last_brace_idx = input_text.rindex("]")
    query = input_text[first_brace_idx : last_brace_idx + 1]  # noqa
    query = query.replace("  ", "")  # To replace unwanted extra spaces
    return update_query(query)




def add_ignore_option_regex(mongo_query: dict):
    """Add options in regex query.


    Args:
        mongo_query (dict): mongo query
    """
    if not isinstance(mongo_query, dict):
        return False
    if "$regex" in mongo_query and "$options":
        mongo_query["$options"] = "i"
        return True
    for key in mongo_query:
        if add_ignore_option_regex(mongo_query[key]):
            break
    return False




def format_output(output) -> str:
    """Parse LLM output response.


    Args:
        output (str): The output of the llm


    Returns:
        str: Gives the corresponding method and query
    """
    input_text = get_pymongo_command(output)


    first_brace_idx = input_text.index("{")
    last_brace_idx = input_text.rindex("}")


    # Find the method part
    method = input_text[: first_brace_idx - 1].split(".")[-1]
    query = input_text[first_brace_idx : last_brace_idx + 1]  # noqa


    query = query.replace("  ", "")  # To replace unwanted extra spaces


    query = update_query(query)


    return method, query
