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

import de.bugplus.development.BugplusProgramImplementation;
import de.bugplus.development.BugplusImplementation;



/**
 * @Author Christian Bartelt
 * @Date 23.01.22 21:37
 * @Version 0.0.1
 */
final public class BugplusProgramSpecificationImpl extends AbstractBugplusSpecification implements BugplusProgramSpecification {


    private BugplusProgramSpecificationImpl() {}

    public BugplusProgramSpecificationImpl(String id, int numDataIn, int numControlOut, BugplusLibrary library) {

        this();

        this.identifier = id;

        this.numDataIn = numDataIn;

        this.numControlOut = numControlOut;

        this.lib = library;

        if (this.lib.containsSpecification(id)) {
            System.out.println("Error: Specification identifier cannot be defined newly because it already exists in knowledge base."); }



    }


    @Override
    public BugplusImplementation getImplementation(int indexSelectedImplementation) {

        if (this.implementations.size()> indexSelectedImplementation) {
            return this.implementations.get(indexSelectedImplementation); }
        else {
            System.out.println("Error: The selected implementation index of specification \"" + this.getIdentifier() + "\" does not exists.");
            return null;
        }
    }

    @Override
    public BugplusLibrary getLibrary() {

        return this.lib;
    }

    @Override
    public BugplusProgramImplementation addImplementation() {


        BugplusProgramImplementation newImplementation = BugplusProgramImplementation.getInstance(this);

        this.implementations.add(newImplementation);

        return newImplementation;
    }
}
