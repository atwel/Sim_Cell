"""
Variant - simultaneous passing (by cell) variant.
A cell is selected to look for action each timestep. Most changes are in the 
activate_random_cell method of the AC_CellNet class and the chain_step 
method in the AC_Cells class.

 This module implements the core logic of action in Padgett and Powell's
model of autocatalysis and hypercycles. Other modules are required for the
model to work, but the Cells and their behaviors are implemented here.


Written by Jon Atwell
"""


import AC_ProductRules


class Cell:

    def __init__(self, urn, productRule_Net, RNG, id,
                    selective_intelligence=False, reproduction_type="source",
                    topology="spatial"):
        """ The contents of the cell. Most things just track what is going
        on with the cell and the global parameters. 
        """

        self.isAlive = True
        self.location = (-1,-1)
        self.neighbors = []               # added after locations are assigned
        self.product_rules = {}
        self.product_netrules = {}
        self.products = {}
        self.count_rules = 0
        self.active_rule = None      # rule used in case it's to be reproduced
        self.id = id
        self.RNG = RNG              # so we can easily reproduce runs.
        self.repro_type= reproduction_type          # key parameter
        self.intel = selective_intelligence              # key parameter
        self.topology = topology                         # key parameter
        self.urn = urn                                         # key parameter
        self.productRule_Net = productRule_Net
        self.cellNet = None         # we'll add this once the cells are made.


    def __str__(self):
        """ Print checks for the version of the model with cell movement.
        """

        return "cell with " + str(self.count_rules) + " rules"


    def set_location(self, x, y):
        """ The method for setting the location of the cell in the space. It's
        used in the static grid setup (no movement) because freshly
        created cells do not have a location.
        """
        
        self.location = (x,y)
        

    def get_location(self):
        """ The method for querying a cell's location.
        """
        
        return self.location


    def add_cellNet(self, net):
        """ This method allows us to provide a handle for the cellNet to
        the cell. It can't be done upon initialization because we make the
        cellNet after we make the cells.
        """

        self.cellNet = net


    def add_Product(self, product):
        """This method allows the cell to put a product in a stack so that it
        can be used later.
        """
        try:
            self.products[product.get_type()].append(product)
        except:
            self.products[product.get_type()] = [product]


    def remove_Product(self, type):
        """ This method allows the cell pull out a product of the requested
        type if it has it in its storage.
        """
        if type in self.products.keys():
            if self.products[type] != []:
                return self.products[type].pop()
        return None


    def has_Product(self):
        """ A method to get a product type from the cell's storage. We need
        to check that there is still a compatible rule for any product because
        there is a very good chance the rule was deleted since the product was
        received. If there are any products and rules that can use them, one 
        is grabbed uniform at random and the type of the product is returned. 
        The product itself will not be returned because it is picked up later.

        """ 
        has = []
        for content in self.products.keys():
            if content in self.product_rules.keys():
                has.extend(self.products[content])
            else:
                self.products[content] = []
        try:
            return self.RNG.sample(has,1)[0].get_type()
        except:
            return None


    def has_rule(self, product):
        """ This method just checks to see if this cell has a rule that is
        compatible with the product it just received. It allows the explicit
        argument to be the product itself or just the integer that identifies
        its type.
        """

        if type(product) == int:
            if product in self.product_rules.keys(): 
                #indexError if no rules for that type
                return True
            else:
                return False
        else:
            if product.get_type() in self.product_rules.keys(): 
                #indexError if no rules for that type
                return True
            else:
                return False


    def add_ProductRule(self, aProductRule):
        """ The method for adding a product rule to the collection the cell
        currently owns.
        """
        
        # making sure nothing inappropriate sneaks in.
        if isinstance(aProductRule, AC_ProductRules.ProductRule):

            # Because we're using dictionaries to hold everything,
            # a nested set of try/except expressions  is used to set the
            # dictionaries up correctly. Possibly rewrite using Collections
            # module dictionaries.

            input = aProductRule.get_input()
            output = aProductRule.get_output()
            try:
                self.product_rules[input][output].append(aProductRule)
            except:
                try:
                    self.product_rules[input][output] = [aProductRule]
                except:
                    self.product_rules[input] = {}
                    self.product_rules[input][output] = [aProductRule]

            # Adding the related NetRule as well.
            try:
                self.product_netrules[aProductRule.get_name()].add_to_count()
            except:
                self.add_ProductNetRule(aProductRule)

            self.count_rules +=1

        else:
            raise TypeError("Argument is not of type AC_Products.ProductRule")
            

    def remove_ProductRule(self, a_ProductRule):
        """ The method used to remove a product rule from the Cell's
        collection.
        """

        # Figuring out what type of rule it is
        input = a_ProductRule.get_input()
        output = a_ProductRule.get_output()

        # This pulls the actual instance out of the cell's collection
        self.product_rules[input][output].remove(a_ProductRule)

        # This removes the rule from the netrules collection by
        # decrementing the count. There is a chance the whole
        # netrule will be removed below.
        self.product_netrules[a_ProductRule.get_name()].subtract_from_count()

        # This count just saves us from having to count the collection
        self.count_rules -= 1

        # Doing some clean up: If that was the last of that type of rule...
        if self.product_rules[input][output] == []:
            # ...we remove it from the cell's netrule collection.
            rule = self.product_netrules.pop(a_ProductRule.get_name(), None)

            # we then remove it from the Net.
            self.productRule_Net.remove_ProductNetRule(rule,
                self.cellNet.master_count)

            # We also remove that key from the outer dictionary
            # in the rules collection. pop() on a dict removes the key.
            self.product_rules[input].pop(output)

            # If the outer dict. is also empty, we remove it as well.
            if self.product_rules[input] == {}:
                self.product_rules.pop(input)
             

    def add_ProductNetRule(self, a_ProductRule):
        """ The method to add a NetRule to the productRule_Net. The bulk of
        the work of adding a new rule happens in the add_ProductNetRule()
        method of the productRule_Net class.
        """

        # A check to make sure nothing that shouldn't be in here slips in.
        if isinstance(a_ProductRule, AC_ProductRules.ProductRule):
            try:
                self.product_netrules[a_ProductRule.get_name()].add_to_count()
            except:
                # If there isn't a netrule yet, we need to create one.
                # This code is only run during model initialization.
                new = AC_ProductRules.ProductNetRule(\
                    a_ProductRule.get_input(), a_ProductRule.get_output(), 1)

                # we set its owner to this cell.
                new.set_owner(self)

                # we add the netrule to the cell's collection.
                self.product_netrules[a_ProductRule.get_name()] = new

                #We also add it to the product rule net.
                self.productRule_Net.add_ProductNetRule(new)
        
        else:
            raise TypeError("Argument is not of type AC_Products.ProductRule")
            
    
    def set_active_rule(self, rule):
        """ A simple method to set the currently active rule in the cell.
        """

        if rule in self.product_rules[rule.get_input()][rule.get_output()]:
            self.active_rule = rule 
        else:
            raise InstanceError("This rule doesn't belong to this cell")


    def reproduce_active_rule(self):
        """ This takes the rule the cell just used and reproduces it.
        """
        r = self.active_rule

        self.add_ProductRule((AC_ProductRules.ProductRule(r.get_input(),
            r.get_output())))
        self.cellNet.last_added_rule = self.cellNet.master_count

        # This is just part of the deal.
        self.cellNet.remove_random_rule()


    def chain_step(self, debug):
        """ This method is used to start up a passing chain. An agent is
        selected at random. It is then asked to select a random rule using
        the get_random_rule() method. It then (tries to) selects an input
        according to the INTELLIGENCE parameter. If it finds a usable
        input in the urn, it transforms it and passes it onto a neighbor.
        """
        self.cellNet.master_count +=1
        if  self.cellNet.master_count % 20000 == 0:
            print "steps: ", self.cellNet.master_count
        
        # now we have a rule and we need to try to get a product it can use
        product = self.remove_Product(self.active_rule.get_input())
        if product == None:
            product = self.urn.request_product(self.active_rule.get_input(), 
                self.intel)

        if product != None: # my_prod == None if the request failed.
            #actually changing the product
            product.apply_ProductRule(self.active_rule)
 
            if self.topology == "spatial":
                # passes to a neighbor in von Neuman neighborhood.
                random_neighbor = self.get_random_neighbor()
            else:
                random_neighbor = self.cellNet.get_random_cell(self)

            random_neighbor.receive_product(self,  
                product,product.get_type(), self, debug)

        else:
            if debug:
                print "%s didn't get the right product, %d" %(str(
                    self.get_location()), self.active_rule.get_input())
            
    
     
    def receive_product(self, sender, product, prohibited_return_output,
        who, debug=False):
        """ This method takes in a product and checks to see if the cell can
        transform it. If it can, it does. If not, it's passed back to the urn.
        """

        #Need to create memory so that the right rule is reproduced later

        self.cellNet.master_count +=1
        if  self.cellNet.master_count % 20000 == 0:
            print "steps: ", self.cellNet.master_count

        start = product.get_type()
        if self.has_rule(start):

            if self.repro_type == "target":
                self.active_rule = self.get_random_rule_of_type(start)
                self.reproduce_active_rule()
                self.active_rule = None

            elif self.repro_type == "source":
                sender.reproduce_active_rule()
                sender.active_rule = None


            self.add_Product(product)


            if debug:
                print "%s passed a %d to %s who transformed it to %d" %(
                    str(who), start, str(self.get_location()),
                    product.get_type())
                
        else:
            if debug:
                mystr = " ".join([str(i) for i in\
                    self.product_netrules.keys()])
                print "%s passed a %d to %s but nothing could be done;%s" %(
                    str(who), product.get_type(),str(self.get_location()), 
                    mystr)
            
            # Passing the unusable product back into the environment (the urn)
            self.urn.return_product(product)


    def add_neighbor(self, neighbor):
        """ A very simple method for adding other cells to this
        cell's list of contacts.
        """

        self.neighbors.append(neighbor)


    def get_random_neighbor(self, who=None):
        """ Selecting another cell from among this cell's von Neuman neighbor.
        The selection is not weighted by the rule count for the cell. This
        method supports the exclusion `pass backs,' (from the cell that give
        this cell the product to transform), through the who argument.
        """

        if who == None:
            return self.RNG.sample(self.neighbors,1)[0]

        elif who in self.neighbors:
            copy_neighbors = list(self.neighbors)
            try:
                copy_neighbors.remove(who)
            except:  
                # because in some scenarios (very, very, very few) 
                # that cell might have died and not be in the list.
                pass
            return self.RNG.sample(copy_neighbors,1)[0]
        else:
            a = ("The `who' argument in " + 
                "get_random_neighbor() method is not a neighbor. ")
            raise TypeError(a)

            
    def get_random_rule(self):
        """ An important method: Sometimes a cell loses a rule because someone
        else created a new rule. We want to remove the actual rule uniform at
        random. This means that it is effectively weighted by netrule type 
        because there can be more than one instance of an actual rule of each
        net rule type.
        """   
        candidates = []

        for input in self.product_rules.keys():
            for output in self.product_rules[input].keys():
                for rule in self.product_rules[input][output]:
                    candidates.append(rule)

        return self.RNG.sample(candidates,1)[0]

    
    def get_random_rule_of_type(self,type):
        """ An important method: When a cell is capable of using an input it
        has received, the rule it ultimately uses is selected uniform-at-
        random from among all of the rules that can possibly use it. This 
        means that it is effectively weighted by netrule type because there 
        can be more than one instance of an actual rule of each net rule type.
        """ 

        candidates = []

        for output in self.product_rules[type].keys():
            for rule in self.product_rules[type][output]:
                    candidates.append(rule)

        return self.RNG.sample(candidates,1)[0]

            
