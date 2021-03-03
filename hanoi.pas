PROCEDURE HANOI(VAL N, F, T, O);
  BEGIN
    IF N = 1 THEN
      WRITELN(F, T)
    ELSE
      BEGIN
        CALL HANOI(N - 1, F, O, T);
        WRITELN(F, T);
        CALL HANOI(N - 1, O, T, F);
      END;
  END;

BEGIN
  CALL HANOI(4, 1, 3, 2);
END.
