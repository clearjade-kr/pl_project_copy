#!/usr/bin/env python
# coding: utf-8

'''Parser (Declaration)'''

class Parser(object):
    # fatalError function, accept function 필요
    # scanner, token variable 필요
    # expression(), simpleExpression(), name()
    
    def mode(self) -> None: #???
        if self.token.tok_id == "in":
            self.token = self.scanner.nextToken()
            if self.token.tok_id == "out":
                self.token = self.scanner.nextToken()
        elif self.token.tok_id == "out":
            self.token = self.scanner.nextToken()
    
    def parameterSpecification(self) -> None:
        self.identifierList()
        self.accept("colon","':' expected")
        self.mode()
        self.name()
    
    def formalPart(self) -> None:
        self.accept("l_par","'(' expected")
        self.parameterSpecification()
        while self.token.tok_id == "semi":
            self.token = self.scanner.nextToken()
            self.parameterSpecification()
        self.accept("r_par","')' expected")
    
    def range(self) -> None:
        self.accept("range","'range' expected")
        self.simpleExpression()
        self.accept("to","'..' expected")
        self.simpleExpression()
    
    def index(self) -> None:
        if self.token.tok_id == "range":
            self.range()
        elif self.token.tok_id == "id":
            self.name()
        else:
            self.fatalError("Index error")
    
    def arrayTypeDefinition(self) -> None:
        self.accept("array","'array' expected")
        self.accept("l_par","'(' expected")
        self.index()
        while self.token.tok_id == "comma":
            self.token = self.scanner.nextToken()
            self.index()
        self.accept("r_par","')' expected")    
        self.accept("of","'of' expected")
        self.name()
    
    def identifierList(self) -> None:
        self.accept("id","identifier expected")
        while self.token.tok_id == "comma":
            self.token = self.scanner.nextToken()
            self.accept("id","identifier expected")
    
    def enumerationTypeDefinition(self) -> None:
        self.accept("l_par","'(' expected")
        self.identifierList()
        self.accept("r_par","')' expected")
    
    def typeDefinition(self) -> None:
        if self.token.tok_id == "l_par":
            self.enumerationTypeDefinition()
        elif self.token.tok_id == "array":
            self.arrayTypeDefinition()
        elif self.token.tok_id == "range":
            self.range()
        elif self.token.tok_id == "id":
            self.name()
        else:
            self.fatalError("Type definition error")
    
    def typeDeclaration(self) -> None:
        self.accept("type","'type' expected")
        self.accept("id", "identifier expected")
        self.accept("is","'is' expected")
        self.typeDefinition()
        self.accept("semi","';' expected")
    
    def numberOrObjectDeclaration(self) -> None:
        self.identifierList()
        self.accept("colon","':' expected")
        if self.token.tok_id == "const":
            # numberDeclaration
            self.token = self.scanner.nextToken()
            self.accept("assign","':=' expected")
            self.expression()
        else:
            # objectDeclaration
            self.typeDefinition()
        self.accept("semi","';' expected")
    
    def basicDeclaration(self) -> None:
        if self.token.tok_id == "type":
            self.typeDeclaration()
        elif self.token.tok_id == "proc":
            self.subprogramBody()
        elif self.token.tok_id == "id":
            self.numberOrObjectDeclaration()
        else:
            self.fatalError("Declaration error")
    
    def subprogramSpecification(self) -> None:
        self.accept("proc", "'procedure' expected")
        self.accept("id","identifier expected")
        if self.token.tok_id == "l_par":
            self.formalPart()
    
    def declarativePart(self) -> None:
        while self.token.tok_id == "type" or self.token.tok_id == "proc" or self.token.tok_id == "id":
            self.basicDeclaration()
    
    def subprogramBody(self) -> None:
        self.subprogramSpecification()
        self.accept("is","'is' expected")
        self.declarativePart()
        self.accept("begin","'begin' expected")
        self.sequenceOfStatements()
        self.accept("end","'end' expected")
        if self.token.tok_id == "id":
            self.token = self.scanner.nextToken()
        self.accept("semi","';' expected")    
            
