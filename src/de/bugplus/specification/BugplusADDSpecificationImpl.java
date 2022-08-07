/*
 * MIT License
 *
 * Bug+ Interpreter
 * Copyright (c) 2022 Christian Bartelt
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package de.bugplus.specification;


import de.bugplus.development.BugplusImplementation;


/**
 * @Author Christian Bartelt
 * @Date 23.01.22 21:37
 * @Version 0.0.1
 */
final class BugplusADDSpecificationImpl extends AbstractBugplusSpecification implements BugplusADDSpecification {

    static BugplusADDSpecification OBJ;

    private BugplusADDSpecificationImpl() {

        this.identifier = "+";
        this.numDataIn = 2;
        this.numControlOut = 2;
    }

    public void addProgram(BugplusImplementation implementation) {

        this.implementations.add(0, implementation);
    }

    static BugplusADDSpecification getInstance() {

        if (OBJ == null) {
            OBJ = new BugplusADDSpecificationImpl(); }

        return OBJ;
    }

    static BugplusADDSpecification getInstance(BugplusImplementation implementation) {

        if (OBJ == null) {
            OBJ = new BugplusADDSpecificationImpl();
            OBJ.addProgram(implementation); }

        return OBJ;
    }


}
