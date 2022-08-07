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

import java.util.List;
import java.util.ArrayList;

import de.bugplus.development.BugplusImplementation;


/**
 * @Author Christian Bartelt
 * @Date 25.01.22 19:51
 * @Version 0.0.1
 */
abstract class AbstractBugplusSpecification implements BugplusSpecification {

    protected String identifier;

    protected int numDataIn = 2;
    protected int numControlOut = 2;

    //Tobi
    //protected int internalState = 0;

    final protected List<BugplusImplementation> implementations = new ArrayList<>();

    protected BugplusLibrary lib;


    //Tobi
    //@Override
    //public int getInternalState() {
     //   return this.internalState;
    //}

    @Override
    public int getNumDataIn() {

        return this.numDataIn;
    }

    @Override
    public int getNumControlOut() {

        return this.numControlOut;
    }


    @Override
    public String getIdentifier() {

        return this.identifier;
    }

    @Override
    public BugplusLibrary getLibrary() {

        return this.lib;
    }

    @Override
    public BugplusImplementation getImplementation(int indexSelectedImplementation) {
        return this.implementations.get(indexSelectedImplementation);
    }

}
