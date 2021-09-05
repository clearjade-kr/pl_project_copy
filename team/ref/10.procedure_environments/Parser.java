// Parameter modes partially completed

import java.util.*;

public class Parser extends Object{

   private Chario chario;
   private Scanner scanner;
   private Token token;
   private SymbolTable table;
   private SubrangeDescriptor BOOL_TYPE, CHAR_TYPE, INT_TYPE;    // Built-in types

   private Set<Integer> addingOperator,
                        multiplyingOperator,
                        relationalOperator,
                        basicDeclarationHandles,
                        statementHandles,
                        leftNames,                        // Sets of roles for names (see below)
                        rightNames;
                        

   public Parser(Chario c, Scanner s){
      chario = c;
      scanner = s;
      initHandles();
      initTypeDescriptors();
      initTable();
      token = scanner.nextToken();
   }

   public void reset(){
      scanner.reset();
      initTable();
      token = scanner.nextToken();
   }

   private void initHandles(){
      addingOperator = new HashSet<Integer>();
      addingOperator.add(Token.PLUS);
      addingOperator.add(Token.MINUS);
      multiplyingOperator = new HashSet<Integer>();
      multiplyingOperator.add(Token.MUL);
      multiplyingOperator.add(Token.DIV);
      multiplyingOperator.add(Token.MOD);
      relationalOperator = new HashSet<Integer>();
      relationalOperator.add(Token.EQ);
      relationalOperator.add(Token.NE);
      relationalOperator.add(Token.LE);
      relationalOperator.add(Token.GE);
      relationalOperator.add(Token.LT);
      relationalOperator.add(Token.GT);
      basicDeclarationHandles = new HashSet<Integer>();
      basicDeclarationHandles.add(Token.TYPE);
      basicDeclarationHandles.add(Token.ID);
      basicDeclarationHandles.add(Token.PROC);
      statementHandles = new HashSet<Integer>();
      statementHandles.add(Token.EXIT);
      statementHandles.add(Token.ID);
      statementHandles.add(Token.IF);
      statementHandles.add(Token.LOOP);
      statementHandles.add(Token.NULL);
      statementHandles.add(Token.WHILE);
      leftNames = new HashSet<Integer>();                 // Name roles for targets of assignment statement
      leftNames.add(SymbolEntry.PARAM);
      leftNames.add(SymbolEntry.VAR);
      rightNames = new HashSet<Integer>(leftNames);       // Name roles for names in expressions
      rightNames.add(SymbolEntry.CONST);
   }

   /*
   New routine for computing the values of static expressions
   */
   SymbolEntry computeValue(int v1, int v2, Token op){
      int result = 0;
      SymbolEntry entry = new SymbolEntry();
      entry.role = SymbolEntry.CONST;
      entry.value = result;
      return entry;
   }

   /*
   Four new routines for type analysis.
   */

   // Sets up the type information for the built-in types
   private void initTypeDescriptors(){
      BOOL_TYPE = new SubrangeDescriptor();
      BOOL_TYPE.setLowerAndUpper(0, 1);
      BOOL_TYPE.setSuperType(BOOL_TYPE);
      CHAR_TYPE = new SubrangeDescriptor();
      CHAR_TYPE.setLowerAndUpper(0, 127);
      CHAR_TYPE.setSuperType(CHAR_TYPE);
      INT_TYPE = new SubrangeDescriptor();
      INT_TYPE.setLowerAndUpper(Integer.MIN_VALUE, Integer.MAX_VALUE);
      INT_TYPE.setSuperType(INT_TYPE);
   }

   // Compares two types for compatibility using name equivalance
   private void matchTypes(TypeDescriptor t1, TypeDescriptor t2, String errorMessage){
      // Need two valid type descriptors to check for an error
      if (t1.form == TypeDescriptor.NONE || t2.form == TypeDescriptor.NONE) return;
      // Exact name equivalence: the two descriptors are identical
      if (t1 == t2) return;
      // Check for two subranges, super types must be identical
      if (t1.form == TypeDescriptor.SUBRANGE && t2.form == TypeDescriptor.SUBRANGE){
         if (((SubrangeDescriptor)t1).superType != ((SubrangeDescriptor)t2).superType)
            chario.putError(errorMessage);
      }
      else
         // A least one record, array, or enumeration, and does not match
         chario.putError(errorMessage);
   }

   // Checks the form of a type against an expected form
   private void acceptTypeForm(TypeDescriptor t, int typeForm, String errorMessage){
      if (t.form == TypeDescriptor.NONE) return;
      if (t.form != typeForm)
         chario.putError(errorMessage);
   }

   /*
   Two new routines for role analysis.
   */

   private void acceptRole(SymbolEntry s, int expected, String errorMessage){
      if (s.role != SymbolEntry.NONE && s.role != expected)
         chario.putError(errorMessage);
   }

   private void acceptRole(SymbolEntry s, Set<Integer> expected, String errorMessage){
      if (s.role != SymbolEntry.NONE && ! (expected.contains(s.role)))
         chario.putError(errorMessage);
   }

   private void accept(int expected, String errorMessage){
      if (token.code != expected)
         fatalError(errorMessage);
      token = scanner.nextToken();
   }

   private void fatalError(String errorMessage){
      chario.putError(errorMessage);
      throw new RuntimeException("Fatal error");
   }

   /*
   Three new routines for scope analysis.
   */

   private void initTable(){
      table = new SymbolTable(chario);
      table.enterScope();
      SymbolEntry entry = table.enterSymbol("BOOLEAN");
      entry.setRole(SymbolEntry.TYPE);
      entry.setType(BOOL_TYPE);
      entry = table.enterSymbol("CHAR");
      entry.setRole(SymbolEntry.TYPE);
      entry.setType(CHAR_TYPE);
      entry = table.enterSymbol("INTEGER");
      entry.setRole(SymbolEntry.TYPE);
      entry.setType(INT_TYPE);
      entry = table.enterSymbol("TRUE");
      entry.setRole(SymbolEntry.CONST);
      entry.setType(BOOL_TYPE);
      entry = table.enterSymbol("FALSE");
      entry.setRole(SymbolEntry.CONST);
      entry.setType(BOOL_TYPE);
   }      

   private SymbolEntry enterId(){
      SymbolEntry entry = null;
      if (token.code == Token.ID)
         entry = table.enterSymbol(token.string);
      else
         fatalError("identifier expected");
      token = scanner.nextToken();
      return entry;
   }

   private SymbolEntry findId(){
      SymbolEntry entry = null;
      if (token.code == Token.ID)
         entry = table.findSymbol(token.string);
      else
         fatalError("identifier expected");
      token = scanner.nextToken();
      return entry;
   }

   public void parse(){
      subprogramBody();
      accept(Token.EOF, "extra symbols after logical end of program");
      table.exitScope();
   }

   /*
   subprogramBody =
         subprogramSpecification "is"
         declarativePart
         "begin" sequenceOfStatements
         "end" [ <procedure>identifier ] ";"
   */
   private void subprogramBody(){
      subprogramSpecification();
      accept(Token.IS, "'is' expected");
      declarativePart();
      accept(Token.BEGIN, "'begin' expected");
      sequenceOfStatements();
      accept(Token.END, "'end' expected");
      table.exitScope();
      if (token.code == Token.ID){
         SymbolEntry entry = findId();
         acceptRole(entry, SymbolEntry.PROC, "procedure name expected");
      }
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   subprogramSpecification = "procedure" identifier [ formalPart ]
   */
   private void subprogramSpecification(){
      accept(Token.PROC, "'procedure' expected");
      SymbolEntry entry = enterId();
      entry.setRole(SymbolEntry.PROC);
      table.enterScope();
      if (token.code == Token.L_PAR)
         formalPart(entry);
   }

   /*
   formalPart = "(" parameterSpecification { ";" parameterSpecification } ")"
   */

   /*
   parameterSpecification = identifierList ":" mode <type>name
   */
   private SymbolEntry parameterSpecification(){
      SymbolEntry list = identifierList();
      list.setRole(SymbolEntry.PARAM);
      accept(Token.COLON, "':' expected");
      if (token.code == Token.IN)
         token = scanner.nextToken();
      if (token.code == Token.OUT)
         token = scanner.nextToken();
      SymbolEntry entry = findId();
      list.setType(entry.type);
      acceptRole(entry, SymbolEntry.TYPE, "type name expected");
      return list;
   }

   /*
   declarativePart = { basicDeclaration }
   */
   private void declarativePart(){
      while (basicDeclarationHandles.contains(token.code))
         basicDeclaration();
   }

   /*
   basicDeclaration = objectDeclaration | numberDeclaration
                    | typeDeclaration | subprogramBody   
   */
   private void basicDeclaration(){
      switch (token.code){
         case Token.ID:
            numberOrObjectDeclaration();
            break;
         case Token.TYPE:
            typeDeclaration();
            break;
         case Token.PROC:
            subprogramBody();
            break;
         default: fatalError("error in declaration part");
      }
   }

   /*
   objectDeclaration =
         identifierList ":" typeDefinition ";"

   numberDeclaration =
         identifierList ":" "constant" ":=" <static>expression ";"
   */
   private void numberOrObjectDeclaration(){
      SymbolEntry list = identifierList();
      accept(Token.COLON, "':' expected");
      if (token.code == Token.CONST){
         list.setRole(SymbolEntry.CONST);
         token = scanner.nextToken();
         accept(Token.GETS, "':=' expected");
         SymbolEntry entry = staticExpression();
         list.setType(entry.type);
         list.setValue(entry.value);
      }
      else{
         list.setRole(SymbolEntry.VAR);
         list.setType(typeDefinition());
      }
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   typeDeclaration = "type" identifier "is" typeDefinition ";"
   */
   private void typeDeclaration(){
      accept(Token.TYPE, "'type' expected");
      SymbolEntry entry = enterId();
      entry.setRole(SymbolEntry.TYPE);
      accept(Token.IS, "'is' expected");
      entry.setType(typeDefinition());
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   typeDefinition = enumerationTypeDefinition | arrayTypeDefinition
                  | range | <type>name
   */
   private TypeDescriptor typeDefinition(){
      TypeDescriptor t = new TypeDescriptor();
      switch (token.code){
         case Token.ARRAY:
            t = arrayTypeDefinition();
            break;
         case Token.L_PAR:
            t = enumerationTypeDefinition();
            break;
         case Token.RANGE:
            t = range();
            break;
         case Token.ID:
            SymbolEntry entry = findId();
            acceptRole(entry, SymbolEntry.TYPE, "type name expected");
            t = entry.type;
            break;
         default: fatalError("error in type definition");
      }
      return t;
   }

   /*
   enumerationTypeDefinition = "(" identifierList ")"
   */
   private TypeDescriptor enumerationTypeDefinition(){
      accept(Token.L_PAR, "'(' expected");
      SymbolEntry list = identifierList();
      list.setRole(SymbolEntry.CONST);
      EnumDescriptor t = new EnumDescriptor();
      t.setIdentifiers(list);
      list.setType(t);
      accept(Token.R_PAR, "')' expected");
      return t;
   }

   /*
   arrayTypeDefinition = "array" "(" index { "," index } ")" "of" <type>name
   */

   /*
   index = range | <type>name
   */
   private TypeDescriptor index(){
      TypeDescriptor t = new TypeDescriptor();      
      if (token.code == Token.RANGE)
         t = range();
      else if (token.code == Token.ID){
         SymbolEntry entry = findId();
         acceptRole(entry, SymbolEntry.TYPE, "type name expected");
         t = entry.type;
         acceptTypeForm(t, TypeDescriptor.SUBRANGE, "index type must be subrange");
         if (t == INT_TYPE) 
            chario.putError("index type cannot be integer");
      }
      else
         fatalError("error in index type");
      return t;
   }

   /*
   range = "range " simpleExpression ".." simpleExpression
   */

   /*
   identifier { "," identifer }
   */
   private SymbolEntry identifierList(){
      SymbolEntry list = enterId();
      while (token.code == Token.COMMA){
         token = scanner.nextToken();
         list.next = enterId();
      }
      return list;
   }

   // Static expressions

   /*
   expression = relation { "and" relation } | { "or" relation }
   */

   /*
   relation = simpleExpression [ relationalOperator simpleExpression ]
   */

   /*
  simpleExpression =
         [ unaryAddingOperator ] term { binaryAddingOperator term }
   */

   /*
   term = factor { multiplyingOperator factor }
   */
   private SymbolEntry staticTerm(){
      SymbolEntry s1 = staticFactor();
      if (multiplyingOperator.contains(token.code))
         matchTypes(s1.type, INT_TYPE, "integer expression expected");
      while (multiplyingOperator.contains(token.code)){
         Token op = token;
         token = scanner.nextToken();
         SymbolEntry s2 = staticFactor();
         matchTypes(s2.type, INT_TYPE, "integer expression expected");
         s1 = computeValue(s1.value, s2.value, op);
      }
      return s1;
   }

   /*
   factor = primary [ "**" primary ] | "not" primary
   */

   /*
   primary = numericLiteral | name | "(" expression ")"
   */
   SymbolEntry staticPrimary(){
      SymbolEntry entry = new SymbolEntry();
      switch (token.code){
         case Token.INT:
            entry.type = INT_TYPE;
            entry.value = token.integer;
            token = scanner.nextToken();
            break;
         case Token.CHAR:
            entry.type = CHAR_TYPE;
            entry.value = token.integer;
            token = scanner.nextToken();
            break;
         case Token.ID:
            entry = findId();
            acceptRole(entry, SymbolEntry.CONST, "constant name expected");
            break;
         case Token.L_PAR:
            token = scanner.nextToken();
            entry = staticExpression();
            accept(Token.R_PAR, "')' expected");
            break;
         default: fatalError("error in primary");
      }
      return entry;
   }

   /*
   sequenceOfStatements = statement { statement }
   */

   /*
   statement = simpleStatement | compoundStatement

   simpleStatement = nullStatement | assignmentStatement
                   | procedureCallStatement | exitStatement

   compoundStatement = ifStatement | loopStatement
   */

   /*
   nullStatement = "null" ";"
   */
   private void nullStatement(){
      accept(Token.NULL, "'null' expected");
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   loopStatement =
         [ iterationScheme ] "loop" sequenceOfStatements "end" "loop" ";"

   iterationScheme = "while" condition
   */

   /*
   ifStatement =
         "if" condition "then" sequenceOfStatements
         { "elsif" condition "then" sequenceOfStatements }
         [ "else" sequenceOfStatements ]
         "end" "if" ";"
   */

   /*
   exitStatement = "exit" [ "when" condition ] ";"
   */
   private void exitStatement(){
      accept(Token.EXIT, "'exit' expected");
      if (token.code == Token.WHEN){
         token = scanner.nextToken();
         condition();
      }
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   assignmentStatement = <variable>name ":=" expression ";"

   procedureCallStatement = <procedure>name [ actualParameterPart ] ";"
   */
   private void assignmentOrCallStatement(){
      SymbolEntry entry = name();
      if (token.code == Token.GETS){
         acceptRole(entry, leftNames, "variable or parameter name expected");
         token = scanner.nextToken();
         TypeDescriptor t2 = expression();
         matchTypes(entry.type, t2, "types are not compatible");
      }
      else
         acceptRole(entry, SymbolEntry.PROC, "procedure name expected");
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   condition = <boolean>expression
   */
   private void condition(){
      TypeDescriptor t = expression();
      matchTypes(t, BOOL_TYPE, "Boolean expression expected");
   }

   /*
   expression = relation { "and" relation } | { "or" relation }
   */

   /*
   relation = simpleExpression [ relationalOperator simpleExpression ]
   */

   /*
  simpleExpression =
         [ unaryAddingOperator ] term { binaryAddingOperator term }
   */

   /*
   term = factor { multiplyingOperator factor }
   */

   /*
   factor = primary [ "**" primary ] | "not" primary
   */

   /*
   primary = numericLiteral | stringLiteral | name | "(" expression ")"
   */

   /*
   name = identifier [ indexedComponent ]
   */
   private SymbolEntry name(){
      SymbolEntry entry = findId();
      if (token.code == Token.L_PAR)
         if (entry.role == SymbolEntry.PROC)
            actualParameterPart(entry);
         else
            entry = indexedComponent(entry);
      return entry;
   }

   /*
   indexedComponent = "(" expression  { "," expression } ")"
   */


   private boolean acceptIndex(TypeDescriptor t, Iterator<TypeDescriptor> indexTypes, 
                                   boolean mismatch){
      if (! indexTypes.hasNext()) return true;
      matchTypes(t, indexTypes.next(), 
                 "type of array index incompatible with declaration");
      return mismatch;
   }

   /*
   actualParameterPart = "(" expression  { "," expression } ")"
   */
   private boolean acceptParameter(TypeDescriptor t, Iterator<SymbolEntry> parameters, 
                                   boolean mismatch){
      if (! parameters.hasNext()) return true;
      matchTypes(t, parameters.next().type, 
                 "type of actual parameter incompatible with type of formal parameter");
      return mismatch;
   }

}
