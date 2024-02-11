package com.apex974.nifi.processors.langchainhelper;

import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.components.PropertyDescriptor.Builder;
import org.apache.nifi.components.PropertyValue;
import org.apache.nifi.annotation.behavior.DynamicProperty;
import org.apache.nifi.annotation.behavior.DynamicRelationship;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.annotation.behavior.ReadsAttribute;
import org.apache.nifi.annotation.behavior.ReadsAttributes;
import org.apache.nifi.annotation.behavior.WritesAttribute;
import org.apache.nifi.annotation.behavior.WritesAttributes;
import org.apache.nifi.annotation.lifecycle.OnScheduled;
import org.apache.nifi.annotation.documentation.CapabilityDescription;
import org.apache.nifi.annotation.documentation.SeeAlso;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.util.StandardValidators;
import org.apache.nifi.components.Validator;
import org.apache.nifi.expression.ExpressionLanguageScope;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;

@Tags({"langchain", "LCEL", "runnable parallel", "LLMs"})
@CapabilityDescription("Create branches for Runnable Parallel in LangChain LCEL")
@SeeAlso({})
@DynamicProperty(name = "Relationship Name", value = "Expression Language expression that returns a boolean value indicating whether or not the FlowFile should be routed to this Relationship",
    expressionLanguageScope = ExpressionLanguageScope.FLOWFILE_ATTRIBUTES,
    description = "Routes FlowFiles whose attributes match the Expression Language specified in the Dynamic Property Value to the Relationship " +
                  "specified in the Dynamic Property Key")
@DynamicRelationship(name = "Name from Dynamic Property", description = "FlowFiles that match the Dynamic Property's Attribute Expression Language")
@ReadsAttributes({@ReadsAttribute(attribute="", description="")})
@WritesAttributes({@WritesAttribute(attribute="", description="")})
public class RunnableParallel extends AbstractProcessor {

    private static final String PREFIX = "langchain.runnable_parallel.";

    private AtomicReference<Set<Relationship>> relationships = new AtomicReference<>();
    private volatile Set<String> dynamicPropertyNames = new HashSet<>();
    private volatile Map<Relationship, PropertyValue> propertyMap = new HashMap<>();

    @Override
    protected void init(final ProcessorInitializationContext context) {
        // Initialize with an empty set of relationships as they will be dynamically determined
        relationships.set(new HashSet<>());
    }

    // public static PropertyDescriptor getDynamicPropertyDescriptor(final String propertyDescriptorName) {
    //     return new Builder()
    //             .name(propertyDescriptorName)
    //             .displayName(propertyDescriptorName)
    //             .description("Runnable Parallel definition for '" + propertyDescriptorName + "'")
    //             .required(false)
    //             .dynamic(true)
    //             .addValidator(Validator.VALID)
    //             .expressionLanguageSupported(ExpressionLanguageScope.ENVIRONMENT)
    //             .build();
    // }

    @Override
    protected PropertyDescriptor getSupportedDynamicPropertyDescriptor(final String propertyDescriptorName) {
        return new PropertyDescriptor.Builder()
                .required(false)
                .name(propertyDescriptorName)
                .displayName(propertyDescriptorName)
                .description("Runnable Parallel definition for '" + propertyDescriptorName + "'")
                .addValidator(Validator.VALID)
                .dynamic(true)
                .expressionLanguageSupported(ExpressionLanguageScope.FLOWFILE_ATTRIBUTES)
                .build();
    }

    @Override
    public Set<Relationship> getRelationships() {
        return relationships.get();
    }

    @Override
    public void onPropertyModified(final PropertyDescriptor descriptor, final String oldValue, final String newValue) {
        final Set<String> newDynamicPropertyNames = new HashSet<>(dynamicPropertyNames);
        if (newValue == null) {
            newDynamicPropertyNames.remove(descriptor.getName());
        } else if (oldValue == null) {    // new property
            newDynamicPropertyNames.add(descriptor.getName());
        }

        this.dynamicPropertyNames = Collections.unmodifiableSet(newDynamicPropertyNames);

        // formulate the new set of Relationships
        final Set<String> allDynamicProps = this.dynamicPropertyNames;
        final Set<Relationship> newRelationships = new HashSet<>();
        for (final String propName : allDynamicProps) {
            if (propName.startsWith(PREFIX)) {
              newRelationships.add(new Relationship.Builder().name(propName.replaceFirst("^" + PREFIX, "")).build());
            }
        }

        this.relationships.set(newRelationships);
    }

    /**
     * When this processor is scheduled, update the dynamic properties into the map
     * for quick access during each onTrigger call
     * @param context ProcessContext used to retrieve dynamic properties
     */
    @OnScheduled
    public void onScheduled(final ProcessContext context) {
        final Map<Relationship, PropertyValue> newPropertyMap = new HashMap<>();
        for (final PropertyDescriptor descriptor : context.getProperties().keySet()) {
            if (!descriptor.isDynamic()) {
                continue;
            }
            getLogger().debug("Adding new dynamic property: {}", new Object[]{descriptor});
            newPropertyMap.put(new Relationship.Builder().name(descriptor.getName()).build(), context.getProperty(descriptor));
        }

        this.propertyMap = newPropertyMap;
    }

    @Override
    public void onTrigger(final ProcessContext context, final ProcessSession session) {
        FlowFile flowFile = session.get();
        if (flowFile == null) {
            return;
        }

        // Route the FlowFile(s) based on the dynamic relationships
        Set<Relationship> dynamicRelationships = this.getRelationships();
        FlowFile firstFlowFile = null;
        Relationship firstRelationship = null;
        if (dynamicRelationships.size() > 1) {
            // More than one relationship, clone and add necessary attributes for merging
            int index = 0;
            String fragmentIdentifier = UUID.randomUUID().toString();
            for (Relationship relationship : dynamicRelationships) {
                FlowFile clone = (index == 0) ? flowFile : session.clone(flowFile);
                clone = session.putAttribute(clone, "langchain.runnable_parallel.key", relationship.getName());
                clone = session.putAttribute(clone, "fragment.identifier", fragmentIdentifier);
                clone = session.putAttribute(clone, "fragment.index", String.valueOf(index));
                clone = session.putAttribute(clone, "fragment.count", String.valueOf(dynamicRelationships.size()));
                if (index != 0) {
                  session.transfer(clone, relationship);
                } else {
                  firstFlowFile = clone;
                  firstRelationship = relationship;}
                index++;
            }
            session.transfer(firstFlowFile, firstRelationship);
        } else if (dynamicRelationships.size() == 1) {
            // Only one relationship, transfer directly
            Relationship relationship = dynamicRelationships.iterator().next();
            flowFile = session.putAttribute(flowFile, "langchain.runnable_parallel.key", relationship.getName());
            session.transfer(flowFile, relationship);
        }
        // No else part needed as there's no default route or strategy to handle no matches
    }
}
