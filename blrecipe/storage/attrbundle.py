"""
Bundles loaded from attributes.msgpack
"""

from sqlalchemy import Column, Integer, Numeric, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import BaseObject


class AttrBundle(BaseObject):  # pylint: disable=too-few-public-methods
    """
    Attribute Bundles as loaded from the attributes msgpack

    A "bundle" entry in the attributes.msgpack can either have a modifier and
    some properties, or a list of bundles and some properties.  That's broken
    down here as either a bundle with a modifier, or a bundle without a modifier
    and an entry in the AttrBundleGroup table keyed by the (bundleName,
    bundleName) key par.
    """

    __tablename__ = 'AttrBundle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True, nullable=False)
    modifier_id = Column(Integer, ForeignKey('AttrModifier.id'))
    target = Column(String(32))
    duration = Column(Numeric, nullable=False, default=0)
    stackable = Column(Boolean)
    isPersistent = Column(Boolean)
    statusEffect = Column(String(32))
    statusEffectCategory = Column(String(32))
    statusEffectDurationImmutable = Column(Boolean)
    statusEffectHidden = Column(Boolean)
    statusEffectHiddenFX = Column(Boolean)
    statusEffectHiddenFXOthers = Column(Boolean)
    statusEffectLevel = Column(Numeric)
    statusEffectRemovalEvent = Column(String(32))
    isGuildBuff = Column(Boolean)
    ignoreFactions = Column(Boolean)
    reduceOnTimeout = Column(Boolean)
    bundleApplicationType = Column(String(32))

    modifier = relationship('AttrModifier', foreign_keys=[modifier_id])
    bundleGroup = relationship('AttrBundleGroup',
                               foreign_keys='[AttrBundleGroup.bundle_id]')

    def __init__(self, name, *args, **kwargs):
        attrs = {key: value for key, value in kwargs.items()
                 if key not in ['bundles', 'modifiers', 'effect']}
        super().__init__(*args, **attrs)
        self.name = name

    def __repr__(self):
        return '<AttrBundle "{}">'.format(self.name)


class AttrBundleGroup(BaseObject):  # pylint: disable=too-few-public-methods
    """
    An aggregation of bundles associated with a bundle.
    """

    __tablename__ = 'AttrBundleGroup'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bundle_id = Column(Integer, ForeignKey('AttrBundle.id'))
    subbundle_id = Column(Integer, ForeignKey('AttrBundle.id'))

    def __init__(self, bundle_id, subbundle_id):
        self.bundle_id = bundle_id
        self.subbundle_id = subbundle_id

    def __repr__(self):
        return '<AttrBundle({}, {}>'.format(self.bundle_id, self.subbundle_id)

