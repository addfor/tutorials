acorn = require 'acorn'

class SemException
    constructor: (@message, @ast) ->

binaryOps =
    "<":  (a,b) -> a <  b
    "<=": (a,b) -> a <= b
    ">":  (a,b) -> a >  b
    ">=": (a,b) -> a >= b
    "==": (a,b) -> a == b
    "!=": (a,b) -> a != b

    "&&": (a,b) -> a && b
    "||": (a,b) -> a || b
    
    "+": (a,b) -> a + b
    "-": (a,b) -> a - b
    "*": (a,b) -> a * b
    "/": (a,b) -> a / b
    "**": (a,b) -> a ** b

compileBlock = (body) ->
    if body.type == "BlockStatement"
        return compileBlock body.body
    if body.length == 1
        return compileAST body[0]
    funcs = for stmt in body
        compileAST stmt
    return (obj) ->
        for func in funcs
            func obj

compileAST = (ast) ->
    if not ast?
        return null
    switch ast.type
        when "Program", "BlockStatement"
            return compileBlock ast.body
            
        when "IfStatement"
            evalCondition = compileAST ast.test
            doConsequent = if ast.consequent? then compileAST ast.consequent
            doAlternate = if ast.alternate? then compileAST ast.alternate

            return (obj) ->
                if evalCondition(obj)
                    if doConsequent? then doConsequent(obj)
                else
                    if doAlternate? then doAlternate(obj)

        when "WithStatement"
            switch ast.object.type
                when "Identifier"
                    name = ast.object.name
                    body = compileBlock ast.body
                    return (obj) -> body(obj[name])
                when "CallExpression"
                    call = ast.object
                    callee = call.callee
                    if callee.type == "Identifier"
                        if callee.name == "recur"
                            if call.arguments.length < 1
                                throw new SemException "Needed at least 1 argument to recur", ast.object
                            
                            getter = compileAST call.arguments[0]
                            body = compileBlock ast.body
                            return (obj) ->
                                curObj = obj
                                while curObj?
                                    body(curObj)
                                    curObj = getter(curObj)
                        else
                            throw new SemException "Invalid with expression function", ast.callee.name
                    else
                        throw new SemException "Invalid with expression", ast.object
            
        when "ExpressionStatement" then return compileAST ast.expression

        when "LogicalExpression", "BinaryExpression"
            opFunc = binaryOps[ast.operator]
            if not opFunc?
                throw new SemException "undefined binary operator: "+ast.operator, ast
            left = compileAST ast.left
            right = compileAST ast.right
            return (obj) -> opFunc left(obj), right(obj)

        when "AssignmentExpression"
            compileAssignmentTo = (lexpr) ->
                switch lexpr.type
                    when "Identifier"
                        memberName = lexpr.name
                        return (obj, value) ->
                            obj[memberName] = value
                    when "MemberExpression"
                        getObject = compileAST lexpr.object
                        setter = compileAssignmentTo lexpr.property
                        return (obj, value) ->
                            setter(getObject(obj), value)
                    else
                        throw new SemException "invalid lvalue", ast
                
            setter = compileAssignmentTo ast.left
            value = compileAST ast.right
            return (obj) -> setter(obj, value(obj))
            
        when "MemberExpression"
            # `object' and `property' are compiled to accessor functions
            getObject = compileAST ast.object
            getProperty = compileAST ast.property
            return (obj) -> getProperty(getObject(obj))
        
        when "Literal"
            value = ast.value
            return () -> value
            
        when "Identifier"
            name = ast.name
            return (obj) -> obj[name]
            
        else
            throw new SemException "forbidden syntax: "+ast.type, ast
            
parseProgram = (text) ->
    ast = acorn.parse text, locations: true
    ast.source = text
    return ast

module.exports = { SemException, compileAST, parseProgram }
    
