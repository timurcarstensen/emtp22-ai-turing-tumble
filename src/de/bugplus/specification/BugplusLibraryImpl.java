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


import java.util.Map;
import java.util.HashMap;

/**
 * @Author Christian Bartelt
 * @Date 23.01.22 21:37
 * @Version 0.0.1
 */
final class BugplusLibraryImpl implements BugplusLibrary {

    private Map<String, BugplusSpecification> functionalKnowledge = new HashMap<String, BugplusSpecification>();


    BugplusLibraryImpl() {

    }

    BugplusLibraryImpl(BugplusSpecification spec) {

        this();
        if (this.functionalKnowledge.containsKey(spec.getIdentifier())) {
            System.out.println("Error: Specification identifier cannot add to knowledge base it already exists in knowledge base."); }
        else {
            this.functionalKnowledge.put(spec.getIdentifier(), spec);}
    }


    @Override
    public boolean containsSpecification(String id) {

        return this.functionalKnowledge.containsKey(id);
    }

    @Override
    public BugplusSpecification selectSpecification(String id) {

        if (this.containsSpecification(id)) {
            return this.functionalKnowledge.get(id);}
        else {
            System.out.println("Error: Specification identifier is unknown in the knowledge base.");
            return null; }
    }

    @Override
    public void addSpecification(BugplusSpecification spec) {

        if (this.functionalKnowledge.containsKey(spec.getIdentifier())) {
            System.out.println("Error: Specification identifier cannot be defined newly because it already exists in knowledge base."); }

        this.functionalKnowledge.put(spec.getIdentifier(), spec);
    }
}
