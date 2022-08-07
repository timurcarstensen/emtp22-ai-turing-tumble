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

package de.bugplus.development;

import de.bugplus.specification.BugplusSpecification;

/**
 * @Author Christian Bartelt
 * @Date 05.02.22 10:43
 * @Version 0.0.1
 */
class BugplusStatementNewBugImpl implements BugplusStatementNewBug {

    protected String specID;
    protected String bugRoleID;

    private BugplusStatementNewBugImpl() {}

    BugplusStatementNewBugImpl(String specificationID, String bugRoleID) {

        this.specID = specificationID;
        this.bugRoleID = bugRoleID;

    }

    @Override
    public void apply(BugplusProgramInstance instance) {

        BugplusSpecification spec = instance.getSpecification().getLibrary().selectSpecification(this.specID);
        BugplusInstance newBug = spec.getImplementation(0).instantiate();
        instance.addBug(this.bugRoleID, newBug);
    }

    @Override
    public String getSpecificationID() {
        return this.specID;
    }

    @Override
    public String getBugRoleID() {
        return this.bugRoleID;
    }

}
