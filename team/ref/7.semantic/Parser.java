// Role analysis partially completed

import java.util.*;

public class Parser extends Object{

   private Chario chario;
   private Scanner scanner;
   private Token token;
   private SymbolTable table;

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
      entry = table.enterSymbol("CHAR");
      entry.setRole(SymbolEntry.TYPE);
      entry = table.enterSymbol("INTEGER");
      entry.setRole(SymbolEntry.TYPE);
      entry = table.enterSymbol("TRUE");
      entry.setRole(SymbolEntry.CONST);
      entry = table.enterSymbol("FALSE");
      entry.setRole(SymbolEntry.CONST);
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
      }
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   subprogramSpecification = "procedure" identifier [ formalPart ]
   */
   private void subprogramSpecification(){
      accept(Token.PROC, "'procedure' expected");
      SymbolEntry entry = enterId();
      table.enterScope();
      if (token.code == Token.L_PAR)
         formalPart();
   }

   /*
   formalPart = "(" parameterSpecification { ";" parameterSpecification } ")"
   */

   /*
   parameterSpecification = identifierList ":" mode <type>name
   */
   private void parameterSpecification(){
      SymbolEntry list = identifierList();
      accept(Token.COLON, "':' expected");
      if (token.code == Token.IN)
         token = scanner.nextToken();
      if (token.code == Token.OUT)
         token = scanner.nextToken();
      SymbolEntry entry = findId();
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
         expression();
      }
      else{
         list.setRole(SymbolEntry.VAR);
         typeDefinition();
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
      typeDefinition();
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   typeDefinition = enumerationTypeDefinition | arrayTypeDefinition
                  | range | <type>name
   */

   /*
   enumerationTypeDefinition = "(" identifierList ")"
   */
   private void enumerationTypeDefinition(){
      accept(Token.L_PAR, "'(' expected");
      SymbolEntry list = identifierList();
      list.setRole(SymbolEntry.CONST);
      accept(Token.R_PAR, "')' expected");
   }

   /*
   arrayTypeDefinition = "array" "(" index ")" "of" <type>name
   */

   /*
   index = range | <type>name
   */
   private void index(){
      if (token.code == Token.RANGE)
         range();
      else if (token.code == Token.ID){
         SymbolEntry entry = findId();
         acceptRole(entry, SymbolEntry.TYPE, "type name expected");
      }
      else
         fatalError("error in index type");
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
         list.append(enterId());
      }
      return list;
   }

   /*
   sequenceOfStatements = statement { statement }
   */
   private void sequenceOfStatements(){
      statement();
      while (statementHandles.contains(token.code))
         statement();
   }

   /*
   statement = simpleStatement | compoundStatement

   simpleStatement = nullStatement | assignmentStatement
                   | procedureCallStatement | exitStatement

   compoundStatement = ifStatement | loopStatement
   */

   /*
   nullStatement = "null" ";"
   */

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

   /*
   assignmentStatement = <variable>name ":=" expression ";"

   procedureCallStatement = <procedure>name [ actualParameterPart ] ";"
   */
   private void assignmentOrCallStatement(){
      SymbolEntry entry = name();
      if (token.code == Token.GETS){
         token = scanner.nextToken();
         expression();
      }
      accept(Token.SEMI, "semicolon expected");
   }

   /*
   condition = <boolean>expression
   */
   private void condition(){
      expression();
   }

   /*
   expression = relation { "and" relation } | { "or" relation }
   */
   private void expression(){
      relation();
      if (token.code == Token.AND)
         while (token.code == Token.AND){
            token = scanner.nextToken();
            relation();
         }
      else if (token.code == Token.OR)
         while (token.code == Token.OR){
            token = scanner.nextToken();
            relation();
         }
   }

   /*
   relation = simpleExpression [ relationalOperator simpleExpression ]
   */
   private void relation(){
      simpleExpression();
      if (relationalOperator.contains(token.code)){
         token = scanner.nextToken();
         simpleExpression();
      }
   }

   /*
  simpleExpression =
         [ unaryAddingOperator ] term { binaryAddingOperator term }
   */
   private void simpleExpression(){
      if (addingOperator.contains(token.code))
         token = scanner.nextToken();
      term();
      while (addingOperator.contains(token.code)){
         token = scanner.nextToken();
         term();
      }
   }

   /*
   term = factor { multiplyingOperator factor }
   */

   /*
   factor = primary [ "**" primary ] | "not" primary
   */

   /*
   primary = numericLiteral | name | "(" expression ")"
   */
   void primary(){
      switch (token.code){
         case Token.INT:
         case Token.CHAR:
         case Token.ID:
            SymbolEntry entry = name();
            break;
         case Token.L_PAR:
            token = scanner.nextToken();
            expression();
            accept(Token.R_PAR, "')' expected");
            break;
         default: fatalError("error in primary");
      }
   }

   /*
   name = identifier [ indexedComponent | selectedComponent ]
   */
   private SymbolEntry name(){
      SymbolEntry entry = findId();
      if (token.code == Token.L_PAR)
         indexedComponent();
      return entry;
   }

   /*
   indexedComponent = "(" expression  { "," expression } ")"
   */

}
