def filter_words(
    df_words, df_rels, df_levels, df_courses, subject_id, level_id, course_id
):
    # start with subject
    allowed = set(df_words[df_words["subject_id"] == subject_id]["word_id"])

    # level filter
    if level_id is not None:
        lvl_allowed = set(df_levels[df_levels["level_id"] == level_id]["word_id"])
        allowed &= lvl_allowed

    # course filter
    if course_id is not None:
        crs_allowed = set(df_courses[df_courses["course_id"] == course_id]["word_id"])
        allowed &= crs_allowed

    df_words_out = df_words[df_words["word_id"].isin(allowed)]
    df_rels_out = df_rels[df_rels["a"].isin(allowed) & df_rels["b"].isin(allowed)]

    return df_words_out, df_rels_out
